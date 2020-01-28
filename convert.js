//const transform = require('graphql-to-json-schema');
const fs = require('fs');
//const { buildSchema, graphqlSync, introspectionQuery } = require("graphql");
//const { buildSchema, graphql, introspectionQuery } = require("graphql");
const graphql = require('graphql');

function usage() {
    console.log("Some usage function");
}

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

    if (!schemaPath) {
	console.error("Missing required parameter $schemaPath");
	process.exit(1);
    }

    fs.readFile(schemaPath, "utf-8", function(err, data) {
	//console.log(data);
	const graphqlSchemaObj = graphql.buildSchema(data);
	const result = graphql.graphqlSync(graphqlSchemaObj, graphql.introspectionQuery).data;
	console.log(JSON.stringify(result));
    });
}
	       
main()
