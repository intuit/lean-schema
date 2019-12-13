# Include everything from the properties file as an env var referencable here
include codegen.properties
export

codegen_full:
	ls -lah queries/intuit_schema.json && apollo codegen:generate --passthroughCustomScalars --schema=queries/intuit_schema.json --queries="queries/**/*.graphql" codegen.full.swift && cp -v ./codegen* /opt/mount

codegen_lean:
	ls -lah lean_schema.json && apollo codegen:generate --passthroughCustomScalars --schema=lean_schema.json --queries="queries/**/*.graphql" --target=swift codegen/

lean_schema:
	node get_types_for_queries.js queries/intuit_schema.json "queries/**/*graphql" | python3 ./decomp.py queries/intuit_schema.json --types-file queries/types.yaml --input-object-depth-level=$(INPUT_OBJECT_DEPTH_LEVEL) | tee lean_schema.json 1> /dev/null

all: lean_schema codegen_lean
	cp -v ./codegen/* /opt/mount
	cp -v lean_schema.json /opt/mount
