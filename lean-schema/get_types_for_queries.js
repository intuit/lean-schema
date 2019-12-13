// NOTE: if not a built-in Node lib, the paths have to be relative to
// node_modules. Then set $NODE_PATH to the prefix path. Ex:
// $NODE_PATH=/usr/local/lib, full path becomes
// /usr/local/lib/node_modules/...
const fs_1 = require('fs');
const path_1 = require('path');
const fetch_schema = require('node_modules/apollo/lib/fetch-schema.js');
//const graphql_1 = fetch_schema.graphql_1;
const graphql_1 = require('graphql')
const loading_1 = require("apollo-codegen-core/lib/loading.js");
const assert = require('assert');
//const _typeFromAST = require('node_modules/apollo/node_modules/graphql/utilities/typeFromAST.js');
const _typeFromAST = require('graphql/utilities/typeFromAST.js');
const _definition = require('graphql/type/definition.js');
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
var _keyMap = require('graphql/jsutils/keyMap.js');
const _keyMap2 = _interopRequireDefault(_keyMap);
const glob = require('glob/glob.js');

/*
Fake rule(s) to hoover up all referenced types from the original Intuit Schema
These are the main rules that use Types:
- /usr/local/lib/node_modules/apollo/node_modules/graphql/validation/rules/FieldsOnCorrectType.js
- /usr/local/lib/node_modules/apollo/node_modules/graphql/validation/rules/FragmentsOnCompositeTypes.js
- /usr/local/lib/node_modules/apollo/node_modules/graphql/validation/rules/KnownTypeNames.js
- /usr/local/lib/node_modules/apollo/node_modules/graphql/validation/rules/ValuesOfCorrectType.js
- /usr/local/lib/node_modules/apollo/node_modules/graphql/validation/rules/VariablesAreInputTypes.js
- UniqueInputFieldNames.js
*/
function getFragmentType(context, name) {
    var frag = context.getFragment(name);
    if (frag) {
	var type = (0, _typeFromAST.typeFromAST)(context.getSchema(), frag.typeCondition);
	if ((0, _definition.isCompositeType)(type)) {
	    return type;
	}
    }
}

function GetAllSchemaTypes(context) {
    return {
	Argument: function Argument(node) {
	    var type = context.getType();
	    var parentType = context.getParentType();
	    if (type) {
		context.types.add(type);
	    }
	    if (parentType) {
		context.types.add(parentType);
	    }
	},
	BooleanValue: function BooleanValue(node) {
	    var inputType = context.getInputType();
	    if (inputType) {
		var type = (0, _definition.getNamedType)(inputType);
		context.types.add(type);
	    }
	},
	Directive: function Directive(node) {},
	DirectiveDefinition: function DirectiveDefinition(node) {},
	Document: function Document(node) {},
	EnumTypeDefinition: function EnumTypeDefinition(node) {},
	EnumTypeExtension: function EnumTypeExtension(node) {},
	EnumValue: function EnumValue(node) {
	    var type = (0, _definition.getNamedType)(context.getInputType());
	    if (type) {
		context.types.add(type);
	    }
	},
	EnumValueDefinition: function EnumValueDefinition(node) {},
	Field: function Field(node) {
	    var type = context.getType();
	    var parentType = context.getParentType();
	    if (type) {
		context.types.add(type);
	    }
	    if (parentType) {
		context.types.add(parentType);
	    }
	},
	FieldDefinition: function FieldDefinition(node) {},
	FloatValue: function FloatValue(node) {
	    var inputType = context.getInputType();
	    if (inputType) {
		var type = (0, _definition.getNamedType)(inputType);
		context.types.add(type);
	    }
	},
	FragmentDefinition: function FragmentDefinition(node) {
	    var type = (0, _typeFromAST.typeFromAST)(context.getSchema(), node.typeCondition);
	    if (type) {
		context.types.add(type);
	    }
	},
	FragmentSpread: function FragmentSpread(node) {
	    var fragName = node.name.value;
	    var fragType = getFragmentType(context, fragName);
	    var parentType = context.getParentType();
	    if (fragType) {
		context.types.add(fragType);
	    }
	    if (parentType) {
		context.types.add(parentType);
	    }
	},
	InlineFragment: function InlineFragment(node) {
	    var typeCondition = node.typeCondition;
	    if (typeCondition) {
		var type = (0, _typeFromAST.typeFromAST)(context.getSchema(), typeCondition);
		if (type) {
		    context.types.add(type);
		}
	    }
	    var parentType = context.getParentType();
	    if (parentType) {
		context.types.add(parentType);
	    }
	    var fragType = context.getType();
	    if (fragType) {
		context.types.add(fragType);
	    }
	},
	InputObjectTypeDefinition: function InputObjectTypeDefinition(node) {},
	InputObjectTypeExtension: function InputObjectTypeExtension(node) {},
	InputValueDefinition: function InputValueDefinition(node) {},
	IntValue: function IntValue(node) {
	    var inputType = context.getInputType();
	    if (inputType) {
		var type = (0, _definition.getNamedType)(inputType);
		context.types.add(type);
	    }
	},
	InterfaceTypeDefinition: function InterfaceTypeDefinition(node) {},
	InterfaceTypeExtension: function InterfaceTypeExtension(node) {},
	ListType: function ListType(node) {},
	ListValue: function ListValue(node) {
	    var type = (0, _definition.getNullableType)(context.getParentInputType());
	    if (type) {
		context.types.add(type);
	    }
	},
	Name: function Name(node) {},
	NamedType: function NamedType(node) {
	    var schema = context.getSchema();
	    var typeName = node.name.value;
	    var type = schema.getType(typeName);
	    if (type) {
		context.types.add(type);
	    }
	},
	NonNullType: function NonNullType(node) {},
	NullValue: function NullValue(node) {
	    var type = context.getInputType();
	    context.types.add(type);
	},
	ObjectField: function ObjectField(node) {
	    var parentType = (0, _definition.getNamedType)(context.getParentInputType());
	    if (parentType) {
		context.types.add(parentType);
	    }
	    var fieldType = context.getInputType();
	    if (fieldType) {
		context.types.add(fieldType);
	    }
	},
	ObjectTypeDefinition: function ObjectTypeDefinition(node) {},
	ObjectTypeExtension: function ObjectTypeExtension(node) {},
	ObjectValue: function ObjectValue(node) {
	    var type = (0, _definition.getNamedType)(context.getInputType());
	    if (!(0, _definition.isInputObjectType)(type)) {
		var inputType = context.getInputType();
		if (inputType) {
		    var type = (0, _definition.getNamedType)(inputType);
		    context.types.add(type);
		}
		return false; // Don't traverse further.
	    }
	    var inputFields = type.getFields();
	    var fieldNodeMap = (0, _keyMap2.default)(node.fields, function (field) {
		return field.name.value;
	    });
	    Object.keys(inputFields).forEach(function (fieldName) {
		var fieldType = inputFields[fieldName].type;
		if (fieldType) {
		    context.types.add(fieldType);
		}
	    });
	},
	OperationDefinition: function OperationDefinition(node) {}, //TODO
	OperationTypeDefinition: function OperationTypeDefinition(node) {},
	ScalarTypeDefinition: function ScalarTypeDefinition(node) {},
	ScalarTypeExtension: function ScalarTypeExtension(node) {},
	SchemaDefinition: function SchemaDefinition(node) {},
	SelectionSet: function SelectionSet(node) {},
	StringValue: function StringValue(node) {
	    var inputType = context.getInputType();
	    if (inputType) {
		var type = (0, _definition.getNamedType)(inputType);
		context.types.add(type);
	    }
	},
	UnionTypeDefinition: function UnionTypeDefinition(node) {},
	UnionTypeExtension: function UnionTypeExtension(node) {},
	Variable: function Variable(node) {},
	VariableDefinition: function VariableDefinition(node) {
	    var type = (0, _typeFromAST.typeFromAST)(context.getSchema(), node.type);
	    if (type) {
		context.types.add(type);
	    }
	    var name = node.variable.name.value;
	    var defaultValue = node.defaultValue;
	    var inputType = context.getInputType();
	    if (inputType) {
		context.types.add(inputType);
	    }
	}
    };
}

function getSchemaTypesForQuery(schema, document, fragments) {
    const rules = [
	GetAllSchemaTypes
    ];
    const typeInfo = new graphql_1.TypeInfo(schema);
    const context = new graphql_1.ValidationContext(schema, document, typeInfo);
    context.types = new Set();

    if (fragments) {
	context._fragments = fragments;
    }

    const visitors = rules.map(rule => rule(context));
    graphql_1.visit(document, graphql_1.visitWithTypeInfo(typeInfo, graphql_1.visitInParallel(visitors)));
    return context.types;
}

async function loadAndParseSchema(schemaFilePath) {
    var x = await fetch_schema.fromFile(schemaFilePath);
    return x;
}

function getAllQueryDocTypes(inputPaths, schemaPath) {
    const document = loading_1.loadAndMergeQueryDocuments(inputPaths, "qbl");
    const schema = loadAndParseSchema(schemaPath).resolve();
    console.log(schema);
    assert.ok(schema, "Schema is null or empty!");
    return getSchemaTypesForQuery(schema, document);
}

function cleanType(type) {
    var strOfType = JSON.stringify(type);
    // Strip out anything not alphabetical or _
    var filtered = Array.from(strOfType).filter(c =>
						(c.charCodeAt(0) >= "a".charCodeAt(0) && c.charCodeAt(0) <= "z".charCodeAt(0))
						||
						(c.charCodeAt(0) >= "A".charCodeAt(0) && c.charCodeAt(0) <= "Z".charCodeAt(0))
						||
						(c == "_"));
    return filtered.join("");
}

/*
How this isn't a built-in is a mystery...
For that matter, wheres .update?
*/
function union(setA, setB) {
    var _union = new Set(setA);
    for (var elem of setB) {
	_union.add(elem);
    }
    return _union;
}


function usage() {
    console.log("Usage: node get_types_for_queries.js $schemaPath $inputPathsGlob");
}

/*
  Start of Main
*/
function main(argv) {
    if (!argv) {
	argv = process.argv.slice(2);
    }

    if (argv.length < 1) {
	usage();
	process.exit(0)
    }
    
    argv.forEach(function(S) {
	if (S === "--help" || S === "-h") {
	    usage();
	    process.exit(0);
	}
    });
    
    var schemaPath = argv[0];
    var inputPathsGlob = argv[1];
    
    if (!schemaPath) {
	console.error("Missing required parameter $schemaPath");
	process.exit(1);
    }
    
    if (!inputPathsGlob) {
	console.error("Missing required parameter $inputPathsGlob");
	process.exit(1);
    }

    var inputPaths = glob.sync(inputPathsGlob);
    var document = loading_1.loadAndMergeQueryDocuments(inputPaths, "qbl");
    var schemaPromise = loadAndParseSchema(schemaPath);
    schemaPromise.then(function(schema) {
	const typeInfo = new graphql_1.TypeInfo(schema);
	
	var visitedTypes = getSchemaTypesForQuery(schema, document);
	var implementationTypes = new Set();
	visitedTypes.forEach(function(T) {
	    var possibleTypes = schema.getPossibleTypes(T);
	    if (possibleTypes) {
		possibleTypes.forEach(function(CT) {
		    implementationTypes.add(CT);
		});
	    }			 
	});
	var allTypes = union(visitedTypes, implementationTypes);
	allTypes.delete(undefined);
	allTypes.delete(null);
    
	var cleanedTypesSet = new Set(Array.from(allTypes).map(type => cleanType(type)));
	cleanedTypesSet.delete("_VInputParsingError_");
	cleanedTypesSet.add("Common_GovernmentId");
	var res = {
	    "types" : Array.from(cleanedTypesSet)
	};
	console.log(JSON.stringify(res));
    });
}

main()
