"""
Create some subset of a GraphQL Schema given some input parameters

"""
__author__ = "prussell"

import argparse
import json
import logging
import os
import queue
import select
import sys
import traceback
import typing
import uuid
import yaml

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
DEFAULT_LOG_FILE = "log.decomp"


class SchemaNode(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.inbound = []
        self.outbound = []

    def __repr__(self):
        return "SchemaNode -> {}".format(self.key)


"""
User defined GraphQL Types. In GraphQL, Object is NOT the root of
the Type heiarchy, it's just one of these

"""
GRAPHQL_DEFINED_TYPES = {"enum", "input_object", "interface", "object", "union"}


class SwiftLanguage(object):
    """
    Data for the Swift Language back-end. Example: if we're
    generating for Swift, how do we handle the V4 Schema BigDecimal
    Type? Answer: replace if with Swift's Decimal type.

    """

    # Mapping between V4 Schema BigDecimal Type and the swift language
    # Decimal Type
    scalars_dict = {"BigDecimal": "Decimal"}
    KEY = "swift"
    # Additional Types that we need to define and add to the
    # sub-schema
    additional_types = {
        "Decimal": {
            "inputFields": None,
            "interfaces": None,
            "possibleTypes": None,
            "kind": "SCALAR",
            "name": "Decimal",
            "description": "Swift's Decimal Type, see https://developer.apple.com/documentation/foundation/decimal",
            "fields": None,
            "enumValues": None,
            # Notify later logic that this type replace BigDecimal and to remove BigDecimal from graph
            "$decomp.type_replaces": "BigDecimal",
        }
    }


LANGUAGES_TABLE = {SwiftLanguage.KEY: SwiftLanguage}


class GraphQLTypeRef(object):
    """
    Proxy Type Reference for a a GraphQL Type.

    Possible fields for a Type seem to be:
    ['kind', 
    'name', 
    'description', 
    'fields', 
    'inputFields', 
    'interfaces', 
    'enumValues', 
    'possibleTypes']

    """

    @classmethod
    def to_dict(cls, kind: str = None, name: str = None, description: str = None):
        return {
            "kind": (kind if kind is not None else cls.kind),
            "name": (name if name is not None else cls.__name__),
            "description": (
                description if description is not None else "GraphQLTypeRef"
            ),
            "fields": (cls.fields if hasattr(cls, "fields") else None),
            "inputFields": (cls.inputFields if hasattr(cls, "inputFields") else None),
            "interfaces": (cls.interfaces if hasattr(cls, "interfaces") else None),
            "enumValues": (cls.enumValues if hasattr(cls, "enumValues") else None),
            "possibleTypes": (
                cls.possibleTypes if hasattr(cls, "possibleTypes") else None
            ),
        }

    @classmethod
    def get_name(cls):
        return cls.name if hasattr(cls, "name") else cls.__name__


class GraphQLObjectTypeRef(GraphQLTypeRef):
    kind = "OBJECT"
    interfaces = []
    fields = []


class GraphQLInterfaceTypeRef(GraphQLTypeRef):
    kind = "INTERFACE"
    fields = []


class GraphQLUnionTypeRef(GraphQLTypeRef):
    kind = "UNION"
    possibleTypes = []


class GraphQLEnumTypeRef(GraphQLTypeRef):
    kind = "ENUM"
    enumValues = []


class GraphQLInputObjectTypeRef(GraphQLTypeRef):
    kind = "INPUT_OBJECT"
    inputFields = []


GRAPHQL_TYPE_REF_DICT = {
    "enum": GraphQLEnumTypeRef,
    "object": GraphQLObjectTypeRef,
    "union": GraphQLUnionTypeRef,
    "input_object": GraphQLInputObjectTypeRef,
    "interface": GraphQLInterfaceTypeRef,
}


def get_typeref_for(kind: str) -> GraphQLTypeRef:
    return GRAPHQL_TYPE_REF_DICT[kind.lower()]


def is_graphql_type_ref(node: dict) -> bool:
    """
    Is this a GraphQL Schema JSON Type reference?

    From testing, all the GraphQL User Defined Types have these fields:
    - kind
    - name

    """
    return (
        "kind" in node
        and "name" in node
        and
        # 'ofType' in node
        # and
        node["kind"].lower() in GRAPHQL_DEFINED_TYPES
    )


def is_scalar_ref(node: dict) -> bool:
    """
    Is this a Scalar reference to the scalar_name Type?

    """
    return "kind" in node and node["kind"].lower() == "scalar"


def get_outbound_type_refs(
    root: dict, res: typing.List[str] = None
) -> typing.List[str]:
    """
    Get all outbound vertex keys for some GraphQL Schema Node.
    Basically an adjacent node reference is defined as:
    A sub-JSON Object with obj['type']['kind'] == OBJECT
    Then the key is obj['type']['name']

    This isn't as clear as in JSON Schema, where all refs are marked
    by $ref.

    """
    if res is None:
        res = []

    stack = [root]
    while stack:
        node = stack.pop()
        if type(node) is list:
            stack.extend(node)
        elif type(node) is dict:
            if is_graphql_type_ref(node):
                res.append(node["name"])
            stack.extend(node.items())
        elif type(node) is tuple:
            stack.append(node[0])
            stack.append(node[1])

    return res


def update_type_refs(root, graph, subgraph_keys, scalars_dict: dict = None):
    """
    Update all outbound refs of a GraphQL schema node to only
    reference things that are in the sub-graph

    """
    if scalars_dict is None:
        scalars_dict = {}

    stack = [root]
    while stack:
        node = stack.pop()
        if type(node) is list:
            stack.extend(node)
        elif type(node) is dict:
            # Is this an Object reference ie another non-Scalar type?
            if is_graphql_type_ref(node):
                # Check name of object and if its allowed inthe subgraph
                node_key = node["name"]
                node_kind = node["kind"]
                if node_key not in subgraph_keys:
                    type_ref = get_typeref_for(node_kind)
                    logging.debug(
                        "Replacing {} with {}, is not in subgraph".format(
                            node_key, type_ref.get_name()
                        )
                    )
                    node["name"] = type_ref.get_name()
                    node["typeref_name"] = node_key

            # Update Scalar Types if we need to
            elif is_scalar_ref(node):
                scalar_key = node["name"]
                if scalar_key in scalars_dict:
                    # Replace with the value
                    scalar_value = scalars_dict[scalar_key]
                    node["name"] = scalar_value

            for key in node:
                value = node[key]
                stack.append(value)


def mk_graph_from_schema(graphql_schema: dict) -> dict:
    """
    Make a simple Adjacency List representation of the Schema Types
    from a GraphQL Schema formatted Object.

    A GraphQL Schema is basically just something that looks like this:
    {"errors" : [],
     "data" : {"__schema" : {..., 'types', ...}}
    }
    or just
    {"__schema" : {..., 'types', ...}}

    """
    # We don't care about anything other than types
    if "data" in graphql_schema:
        types = graphql_schema["data"]["__schema"]["types"]
    elif "__schema" in graphql_schema:
        types = graphql_schema["__schema"]["types"]
    elif "types" in graphql_schema:
        types = graphql_schema["types"]
    else:
        raise ValueError("Invalid GraphQL Schema, must have a 'types' section")
    adj = {}

    for T in types:
        K = T["name"]
        V = T
        node = SchemaNode(K, V)
        node.outbound = get_outbound_type_refs(T)
        adj[K] = node

    for K in adj:
        node = adj[K]
        for K2 in node.outbound:
            node2 = adj[K2]
            node2.inbound.append(K)

    return adj


def load_schema(file_path: str):
    with open(file_path) as ifile:
        return json.load(ifile)


def convert_type_path_key(type_path: str, sep="/") -> str:
    """
    Convert some Intuit Type path key to GraphQL Schema Type key.
    Ex: '/network/Contact' -> 'Network_Contact'
    """
    return "_".join(t[0].upper() + t[1:] for t in type_path.split(sep) if t)


def get_subtypes_of_domain(schema, domain, key_func=convert_type_path_key) -> list:
    """
    Q&D version of this, just examine the paths of each type

    """
    R = []
    norm_domain = key_func(domain)

    for type_path in schema:
        if type_path.startswith(norm_domain):
            R.append(type_path)

    return R


def reduce_graphql_schema(schema, graph, subgraph_keys):
    """
    Reduce the GraphQL Schema to only include what's in the computed
    sub-graph

    """
    # Get root set
    schema["__schema"]["types"] = [
        graph[key].value for key in subgraph_keys if key in graph
    ]
    return schema


def all_scalar_types(root):

    stack = [root]
    R = set()

    while stack:

        node = stack.pop()

        if type(node) is list:
            stack.extend(node)

        elif type(node) is dict:
            if "kind" in node and node["kind"].lower() == "scalar":
                R.add(node["name"])

            stack.extend(node.items())

        elif type(node) is tuple:
            stack.append(node[0])
            stack.append(node[1])

    return R


def get_neighboring_types(G: dict, type_key, depth_level):
    Q = queue.Queue()
    Q.put((type_key, 0))
    seen = set()

    while not Q.empty():
        (node_key, depth) = Q.get()

        if node_key not in seen:
            seen.add(node_key)

            if depth >= depth_level:
                continue

            if node_key in G:
                node_val = G[node_key]
                for neighbor in node_val.outbound:
                    Q.put((neighbor, depth + 1))
            else:
                logging.warning(
                    "Invalid Type Key {} not in Schema, cannot find any neighboring Types for it".format(
                        node_key
                    )
                )

    return seen


def get_types_from_file(G: dict, types_file: dict, types_set: set = None) -> set:
    """
    Get additional User-specified Types from a object from a file.

    @param types_file: the object loaded from the --types-file CLI parameter

    return: the set of additional Types constructed from the YAML specification

    """
    if types_set is None:
        types_set = set()

    if "types" in types_file:
        types_from_file = types_file["types"]
        if type(types_from_file) is str:
            types_set.add(convert_type_path_key(types_from_file))
        elif type(types_from_file) is list:
            for subtype in types_from_file:
                # Allow String or dict in the Types
                if type(subtype) is str:
                    types_set.add(convert_type_path_key(subtype))
                elif type(subtype) is dict and len(subtype.keys()) == 1:
                    type_key = list(subtype.keys())[0]
                    if "depth" in subtype[type_key]:
                        depth = int(subtype[type_key]["depth"])
                        neighbors = get_neighboring_types(
                            G, convert_type_path_key(type_key), depth
                        )
                        types_set.update(neighbors)
        else:

            error_msg = "Unrecognized value for key 'types' in file {}, must have type list or str, but is {}".format(
                types_file, type(types_from_file)
            )
            logging.error(error_msg)
            raise ValueError(error_msg)

    # Load all types of domain
    if "domains" in types_file:
        for domain in types_file["domains"]:
            types_set.update(get_subtypes_of_domain(G, convert_type_path_key(domain)))

    return types_set


def get_types_from_input():
    """
    Check any input JSON for additional Types
    """
    types = set()

    if select.select([sys.stdin], [], [], 0.0)[0]:
        text_in = sys.stdin.read()
        if text_in.strip():
            logging.debug("Additional keys from stdin: {}".format(text_in))
            types.update(json.loads(text_in)["types"])
    else:
        logging.debug("No additional subgraph keys from stdin")

    return types


def check_input_object_depth_level(value):
    try:
        if int(value) < 0:
            raise ValueError
    except:
        if value is None or value == "":
            return 0
        else:
            raise argparse.ArgumentTypeError("{} must be an integer >= 0".format(value))

    return int(value)


def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument("SCHEMA_FILE", help="Path to the Intuit Schema JSON file")
    parser.add_argument(
        "--types-file", help="Path to the (optional) Types YAML file", default=None
    )
    parser.add_argument(
        "--log-level",
        help="The log level for all non-JSON output",
        choices=LOG_LEVELS.keys(),
        default="ERROR",
    )
    parser.add_argument(
        "--log-file",
        help="The file to log all non-JSON output to",
        default=DEFAULT_LOG_FILE,
    )
    parser.add_argument(
        "--input-object-depth-level",
        help="The level of Type references to include for GraphQL InputObjects. If certain Types are missing in the generated code, try setting this to 1 or 2. All transitive Types up to N levels away will be included.",
        default=0,
        type=check_input_object_depth_level,
    )
    parser.add_argument(
        "--target-language",
        help="The target Programming Language. It's toolchain will consume the output LeanSchema and generate code. Ex: Apollo Codegen generates Swift, TypeScript and Scala code",
        choices=LANGUAGES_TABLE.keys(),
        default=SwiftLanguage.KEY,
    )
    args = parser.parse_args(args)

    with open(args.SCHEMA_FILE, encoding="utf-8") as ifile:
        schema = json.load(ifile)

    schema = schema["data"] if "data" in schema else schema

    # Types file is optional, data can come from stdin or it
    types_file = {}
    if args.types_file is not None:
        types_file_path = os.path.abspath(args.types_file)
        if os.path.exists(types_file_path):
            with open(types_file_path, encoding="utf-8") as ifile:
                types_file = yaml.load(ifile.read()) or {}

    try:
        log_level = LOG_LEVELS[args.log_level]
    except KeyError:
        print(
            "Invalid logging level {}, use one of {}".format(args.log_level, LOG_LEVELS)
        )
        exit(1)

    logfile_path_prefix = os.path.split(args.log_file)[0]
    if logfile_path_prefix and not os.path.exists(logfile_path_prefix):
        print("Log file directory {} does not exist".format(logfile_path_prefix))
        exit(1)

    log_file = args.log_file or DEFAULT_LOG_FILE

    logging.basicConfig(filename=log_file, level=log_level)
    logging.getLogger().addHandler(logging.StreamHandler())
    run_uuid = uuid.uuid4()
    logging.debug("START run {}".format(run_uuid))

    logging.debug("Adding GraphQLTypeRef types to Schema")
    for typeref_type in GRAPHQL_TYPE_REF_DICT.values():
        schema["__schema"]["types"].append(typeref_type.to_dict())

    graph = mk_graph_from_schema(schema)
    # Load all directly stated Types/Domains from file
    root_keys = set()
    types_size = 0
    root_keys.update(get_types_from_file(graph, types_file))
    types_size = len(root_keys)
    logging.debug(
        "Types increased from 0 to {} from types-from-file".format(types_size)
    )

    # Get any additional Root Keys specified from stdin
    try:
        root_keys.update(get_types_from_input())
    except:
        logging.debug(traceback.format_exc())
        logging.error("Error reading type keys from stdin, is it valid JSON?")
        exit(1)
    logging.debug(
        "Types increased from {} to {} from types-from-input".format(
            types_size, len(root_keys)
        )
    )
    types_size = len(root_keys)

    # Get the set of keys for the valid subgraph
    subgraph_keys = {obj.get_name() for obj in GRAPHQL_TYPE_REF_DICT.values()}
    subgraph_keys.update(root_keys)

    # Stuff like {'BigDecimal', 'Boolean', 'Float', 'ID', 'Int',
    # 'Long', 'String'} is defined in the Schema, so have to add it
    # back
    subgraph_keys.update(all_scalar_types(schema))
    logging.debug(
        "Types increased from {} to {} by adding all scalar types".format(
            types_size, len(subgraph_keys)
        )
    )
    types_size = len(subgraph_keys)
    # 'Hard-coded' types to add
    subgraph_keys.add("Schema_Schema_StringSchema0")
    logging.debug(
        "Types increased from {} to {} by adding hard-coded types".format(
            types_size, len(subgraph_keys)
        )
    )
    types_size = len(subgraph_keys)

    # Unfold InputObjects up to some depth
    for input_object in [
        k
        for k in subgraph_keys
        if k in graph and graph[k].value["kind"] == "INPUT_OBJECT"
    ]:
        nset = get_neighboring_types(graph, input_object, args.input_object_depth_level)
        subgraph_keys.update(nset)

    logging.debug(
        "Types increased from {} to {} by unfolding InputObjects to depth = {}".format(
            types_size, len(subgraph_keys), args.input_object_depth_level
        )
    )

    # Prune/clean up subraph by removing references to Types not in
    # the subraph. Also replace any Scalar Types that don't exist for
    # our target language.
    target_language = LANGUAGES_TABLE[args.target_language]
    # Add all additional type from the target language, if any
    if hasattr(target_language, "additional_types"):
        for tkey in target_language.additional_types:
            tvalue = target_language.additional_types[tkey]
            schema_node = SchemaNode(tkey, tvalue)
            graph[tkey] = schema_node
            subgraph_keys.add(tkey)
            if "$decomp.type_replaces" in tvalue:
                replaced_type = tvalue["$decomp.type_replaces"]
                if replaced_type in graph:
                    del graph[replaced_type]
                    subgraph_keys.remove(replaced_type)
                else:
                    logging.warning(
                        "Cannot remove Scalar Type {}, does it exist in Schema?".format(
                            replaced_type
                        )
                    )

    for key in subgraph_keys:
        if key in graph:
            node = graph[key].value
            update_type_refs(
                node, graph, subgraph_keys, scalars_dict=target_language.scalars_dict
            )
            assert graph[key].value == node
        else:
            logging.warning(
                "Bad Type key, is it defined in the Schema?: {}".format(key)
            )

    # Shrink the schema to only include whats in the subgraph
    reduce_graphql_schema(schema, graph, subgraph_keys)

    logging.debug("END run {}".format(run_uuid))
    print(json.dumps(schema))
    return schema


if __name__ == "__main__":
    main(sys.argv[1:])
