"""
# Input
A Collection<GraphQLQuery> and a GraphQL Schema.

# Process
## Visit
For-each GraphQLQuery, parse it into a Document. Visit each Document
using the AllTypesVisitor to get all directly referenced Types in the
Document. Build a Set<Type> as you go and return that.

## Expansion
For-each directly referenced Type, Expand it based on rules such as:

1. If the Type is a Generic Type, then 'unfold' the Type until we
reach a Concrete Type. Ex: List<String> -> String

2. If the Type is an Interface Type, then find all Concrete Types that
implement the Interface. At least one of them will be referenced.

Other expansion rules can apply.

# Output
A Set<String> of Type Names that are referenced, or should be
referenced according to our Type Expansion rules.

The Output of this program is the Input to the Decomp program, which
actually breaks down the Graph by using the referenced Types as Roots.

"""

__author__ = "prussell"

import json
import os
import sys
import typing
import argparse
import enum
import graphql
from graphql.language import DocumentNode, visit
from graphql.language.visitor import TypeInfoVisitor
from graphql.utilities import TypeInfo
from graphql.validation.validation_context import ValidationContext
from lean_schema.project_logging import logger
from lean_schema.visitors import AllTypesVisitor


class ExitErrorCodes(enum.Enum):
    """
    Exit codes for the get_types.py program

    """

    OK = 0
    SCHEMA_FILE_NOT_EXISTS = 1
    SCHEMA_FILE_NOT_A_FILE = 2
    QUERY_PATH_NOT_EXISTS = 3
    QUERY_PATH_NOT_FILE_OR_DIRECTORY = 4


def load_schema(schema_path):
    """Load the Intuit Schema. Apparently it differs a bit from what
    Graphene wants, specifically Graphene doesn't recognize the
    top-level "errors" and "data" fields
    """

    with open(os.path.abspath(schema_path)) as ifile:
        ischema = json.load(ifile)
    if "data" in ischema:
        ischema = ischema["data"]
    return graphql.build_client_schema(ischema)


def visit_document_file(query_path, schema):
    with open(os.path.abspath(query_path)) as ifile:
        doc = ifile.read()

    return visit_document(graphql.parse(doc), schema)


def visit_document(document_ast: DocumentNode, schema):

    if not document_ast or not isinstance(document_ast, DocumentNode):
        raise TypeError("You must provide a document node.")
    # If the schema used for validation is invalid, throw an error.
    type_info = TypeInfo(schema)
    context = ValidationContext(schema, document_ast, type_info)
    # This uses a specialized visitor which runs multiple visitors in parallel,
    # while maintaining the visitor skip and break API.

    # Visit the whole document with each instance of all provided rules.
    # A single document can have multiple Fragments, and we assume a single Query
    all_types = set()
    for def_ast in document_ast.definitions:
        visitor = AllTypesVisitor(context)
        visit(def_ast, TypeInfoVisitor(type_info, visitor))
        all_types.update(visitor.types)

    return all_types


def get_named_type(_type):
    """Equivalent of this function from the Facebook GrapHQL lib from graphql/type/definitions.js:
function getNamedType(type) {
  /* eslint-enable no-redeclare */
  if (type) {
    var unwrappedType = type;
    while (isWrappingType(unwrappedType)) {
      unwrappedType = unwrappedType.ofType;
    }
    return unwrappedType;
  }
}

    Basically we need to 'un-wrap' Type References that are
    generic/composite. The JS GraphQL lib defines a Wrapping Type
    (currently) as a ListType or GraphQLNonNull

    """
    unwrapped_type = _type
    while hasattr(unwrapped_type, "of_type"):
        unwrapped_type = unwrapped_type.of_type

    return unwrapped_type


def expand_type(_type, schema, type_names: set = None) -> typing.Set[str]:
    if type_names is None:
        type_names = set()

    if hasattr(_type, "name"):
        type_names.add(_type.name)
        try:
            for sub_type in schema.get_possible_types(_type):
                type_names.add(sub_type.name)
        except KeyError:
            logger.debug("No sub-types for %s", _type.name)

    if hasattr(_type, "of_type"):
        type_names.add(get_named_type(_type).name)

    return type_names


def expand_types(types, schema) -> typing.Set[str]:
    type_names = set()
    for _type in types:
        if _type:
            type_names.update(expand_type(_type, schema, type_names))

    return type_names


def visit_document_directory(
    root_path: str, schema, file_extensions=("graphql", "gql"), all_types: set = None
) -> set:
    if all_types is None:
        all_types = set()

    for root, _, files in os.walk(root_path):
        for filename in files:
            if filename.split(".")[-1] in file_extensions:
                full_path = os.path.join(root, filename)
                logger.debug("Processing file %s", full_path)
                all_types.update(visit_document_file(full_path, schema))

    return all_types


def main(main_args):
    parser = argparse.ArgumentParser(main_args)
    parser.add_argument("SCHEMA_FILE", help="The Schema File to load")
    parser.add_argument(
        "INPUT_TLD", help="Top-level-directory of the set of Queries to process"
    )
    parser.add_argument(
        "--verbose", help="Verbose output, DEBUG and below", action="store_true"
    )
    parser.add_argument(
        "--sorted", help="Sort the output type names", action="store_true"
    )
    args = parser.parse_args()

    if not args.verbose:
        logger.setLevel("WARNING")

    if not os.path.exists(os.path.abspath(args.SCHEMA_FILE)):
        print(
            "SCHEMA_FILE does not exist: {}".format(args.SCHEMA_FILE), file=sys.stderr
        )
        sys.exit(ExitErrorCodes.SCHEMA_FILE_NOT_EXISTS)

    if not os.path.isfile(os.path.abspath(args.SCHEMA_FILE)):
        print("SCHEMA_FILE is not a file: {}".format(args.SCHEMA_FILE), file=sys.stderr)
        sys.exit(ExitErrorCodes.SCHEMA_FILE_NOT_A_FILE)

    abs_input_tld = os.path.abspath(args.INPUT_TLD)
    if not os.path.exists(abs_input_tld):
        print("INPUT_TLD does not exist: {}".format(args.INPUT_TLD), file=sys.stderr)
        sys.exit(ExitErrorCodes.QUERY_PATH_NOT_EXISTS)

    input_is_file = os.path.isfile(abs_input_tld)
    if not input_is_file and not os.path.isdir(abs_input_tld):
        print(
            "INPUT_TLD is not a file or directory: {}".format(args.INPUT_TLD),
            file=sys.stderr,
        )
        sys.exit(ExitErrorCodes.QUERY_PATH_NOT_FILE_OR_DIRECTORY)

    schema = load_schema(os.path.abspath(args.SCHEMA_FILE))
    all_types = set()
    # Support both single file / top-level-directory
    if input_is_file:
        all_types.update(visit_document_file(abs_input_tld, schema))
    else:
        visit_document_directory(abs_input_tld, schema, all_types=all_types)

    type_names = expand_types(all_types, schema)

    return json.dumps({"types": list(type_names)}, indent=2)


if __name__ == "__main__":
    print(main(sys.argv[1:]))
