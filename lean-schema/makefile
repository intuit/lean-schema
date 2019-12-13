# Include everything from the properties file as an env var referencable here
include codegen.properties
include codegen.vars
export

test:
	echo $(GRAPHQL_QUERIES_DIR)

clean:
	- find . -name "*~" | xargs rm
	- rm -rf __pycache__
	- rm -rf .pytest_cache/
	- rm ./*.scala
	- rm ./*.swift
	- echo "" > apollo.log
	- find . -name __generated__ | xargs rm -rf
	- rm -rf ./queries/*

codegen_full:
	ls -lah queries/intuit_schema.json && apollo codegen:generate --passthroughCustomScalars --schema=queries/intuit_schema.json --queries="queries/**/*.graphql" codegen.full.swift && cp -v ./codegen* /opt/mount

codegen_lean:
	ls -lah lean_schema.json && apollo codegen:generate --passthroughCustomScalars --schema=lean_schema.json --queries="queries/**/*.graphql" --target=swift codegen/

lean_schema:
	node get_types_for_queries.js queries/intuit_schema.json "queries/**/*graphql" | python3 ./decomp.py queries/intuit_schema.json --types-file queries/types.yaml --input-object-depth-level=$(INPUT_OBJECT_DEPTH_LEVEL) | tee lean_schema.json 1> /dev/null

all: lean_schema codegen_lean
	cp -v ./codegen/* /opt/mount
	cp -v lean_schema.json /opt/mount

docker_build:
	docker build -t leanschema .

docker_codegen:
	cp -r $(GRAPHQL_QUERIES_DIR) $(DOCKER_BUILD_QUERIES_DIR)
	cp $(INTUIT_SCHEMA_FILE) $(DOCKER_BUILD_QUERIES_DIR)/intuit_schema.json
	bash ./copy_types_yaml.sh "$(TYPES_YAML_FILE)" $(DOCKER_BUILD_QUERIES_DIR)/types.yaml
	docker run -v $(CURDIR)/$(DOCKER_BUILD_QUERIES_DIR):/opt/intuit/pte/leanschema/queries -v $(CURDIR)/codegen:/opt/mount -e INPUT_OBJECT_DEPTH_LEVEL leanschema make all && echo "Wrote output files to $(CURDIR)/codegen"
	python post_process.py --copy-unmatched-files-dir=$(COPY_UNMATCHED_FILES_DIR) --copy-codegen-files=$(COPY_GENERATED_FILES_AFTER_CODEGEN) ./codegen $(GRAPHQL_QUERIES_DIR)

docker_codegen_full:
	docker run -v $(CURDIR)/codegen:/opt/mount leanschema make codegen_full && echo "Wrote output files to $(CURDIR)/codegen"
