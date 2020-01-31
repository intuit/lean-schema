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

clean:
	- find . -name "*~" | xargs rm
	- rm -rf lean_schema/__pycache__
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

apollo:
	- which apollo || npm install -g apollo@$(APOLLO_PACKAGE_VERSION)

python3:
	- ./install_python3.sh
	- python3 -m venv $(VENV_DIR)
	- $(PIP3) install -r requirements.txt

install: apollo python3
	- $(PIP3) install .

codegen: lean_schema
	ls -lah lean_schema.json && apollo client:codegen --passthroughCustomScalars --localSchemaFile=lean_schema.json --queries="queries/**/*.graphql" --target=swift codegen/
	$(PYTHON3) ./lean_schema/post_process.py --copy-unmatched-files-dir=$(COPY_UNMATCHED_FILES_DIR) --copy-codegen-files=$(COPY_GENERATED_FILES_AFTER_CODEGEN) ./codegen $(GRAPHQL_QUERIES_DIR)

lean_schema:
	./check_graphqljson.sh $(INTUIT_SCHEMA_FILE)
	- mkdir queries/
	cp $(INTUIT_SCHEMA_FILE) queries/intuit_schema.json
	find $(GRAPHQL_QUERIES_DIR) -name '*.graphql' | xargs -I % cp % ./queries/
	find $(GRAPHQL_QUERIES_DIR) -name '*.gql' | xargs -I % cp % ./queries/
	#bash ./copy_types_yaml.sh "$(TYPES_YAML_FILE)" queries/types.yaml
	$(PYTHON3) ./lean_schema/get_types.py queries/intuit_schema.json queries/ | $(PYTHON3) ./lean_schema/decomp.py queries/intuit_schema.json --types-file queries/types.yaml --input-object-depth-level=$(INPUT_OBJECT_DEPTH_LEVEL) | tee lean_schema.json 1> /dev/null
