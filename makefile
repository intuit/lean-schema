# Include everything from the properties file as an env var referencable here
include codegen.properties
export

VENV_DIR = ./venv
PYTHON3 = $(VENV_DIR)/bin/python3
PIP3 = $(VENV_DIR)/bin/pip3
PYTEST = $(VENV_DIR)/bin/python3 -m pytest
APOLLO_PACKAGE_VERSION=2.22.0

.PHONY: lean_schema test clean install codegen

test:
	$(PIP3) install -r requirements.txt
	$(PIP3) install -r test.requirements.txt
	$(PYTEST) tests/

install:
	python3 -m venv $(VENV_DIR)
	npm install -g apollo@$(APOLLO_PACKAGE_VERSION)
	$(PIP3) install --upgrade pip
	$(PIP3) install -r requirements.txt

codegen: lean_schema
	ls -lah lean_schema.json && apollo client:codegen --passthroughCustomScalars --localSchemaFile=lean_schema.json --queries="queries/**/*.graphql" --target=swift codegen/
	$(PYTHON3) ./lean_schema/post_process.py --copy-unmatched-files-dir=$(COPY_UNMATCHED_FILES_DIR) --copy-codegen-files=$(COPY_GENERATED_FILES_AFTER_CODEGEN) ./codegen $(GRAPHQL_QUERIES_DIR)

lean_schema:
	./check_graphqljson.sh $(GRAPHQL_SCHEMA_FILE)
	- mkdir queries/
	cp $(GRAPHQL_SCHEMA_FILE) queries/graphql_schema.json
	find $(GRAPHQL_QUERIES_DIR) -name '*.graphql' | xargs -I % cp % ./queries/
	find $(GRAPHQL_QUERIES_DIR) -name '*.gql' | xargs -I % cp % ./queries/
	bash ./copy_types_yaml.sh "$(TYPES_YAML_FILE)" queries/types.yaml
	$(PYTHON3) -m lean_schema.get_types queries/graphql_schema.json queries/ | $(PYTHON3) -m lean_schema.decomp queries/graphql_schema.json --types-file queries/types.yaml --input-object-depth-level=$(INPUT_OBJECT_DEPTH_LEVEL) | tee lean_schema.json 1> /dev/null

clean:
	- find . -name "*~" | xargs rm
	- rm -rf .pytest_cache/
	- rm ./*.scala
	- rm ./*.swift
	- echo "" > apollo.log
	- find . -name __generated__ | xargs rm -rf
	- rm -rf ./queries/*
	- rm -rf ./queries/.[!.]*
	- rm -rf ./codegen/
	- rm ./lean_schema.json
	- rm ./log.decomp
	- rm ./apollo.log
	- rm -rf lean_schema.egg-info
	- find . -name __pycache__ | xargs rm -rf
	- rm -rf ./node_modules
	- rm package-lock.json
	- rm -rf cov_html/
	- rm -rf venv/
