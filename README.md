
# Intuit Lean Schema

| LeanSchema Version | Supported Apollo Version(s) |
| ------------- |:-------------:|
| 2.0.1      | 2.22.0 | 

## Coverage
```bash
Name        Stmts   Miss  Cover
-------------------------------
decomp.py     319     31    90%
```

## Overview
Welcome to Intuit LeanSchema! LeanSchema is a tool to shrink your GraphQL Schema for your production Mobile Applications. If you have a semi-large Schema (say, > 100 Types) then LeanSchema will help you reduce your Mobile App sizes and reduce your compilation times.

### Sure, but what does this **do**?
It takes a set of GraphQL Queries and a GraphQL Schema as input and produces a much **smaller** Lean Schema. The lean GraphQL Schema is passed to Apollo Client/Codegen to generate iOS Swift Code.

**Any** application/service/library/widget that uses the a large GraphQL Schema can benefit. Here's a real-life example for the Intuit QuickBooks Self-Employed Mobile iOS App:
```
GraphQL Query folder size:
Full Schema : 7.1 MB
Lean Schema : 1.8 MB

Swift compile times clean build:
Full Schema : 526 seconds
Lean Schema : 216 seconds
```
LeanSchema reduced the amount of generated Swift code by 75% and reduced compile time by 50%.

### Who's using this?
LeanSchema is used by many Production Mobile Apps at Intuit, including (but not limited to):
- QuickBooks Self-Employed
- Payments Mobile
- Turbo Mobile

## Requirements
- [Python](https://www.python.org/downloads/) >= 3.7.3.
- [NPM](https://www.npmjs.com/get-npm) >= 6.13.7.
- A set of GraphQL queries compatible with `Apollo v2.22.0`. Any set of valid GraphQL queries **should** work.

### Install Requirements on Mac OS
```bash
brew install python
brew upgrade python
brew install npm
brew upgrade npm
```

## Get the Code
[Download a release](https://github.com/intuit/lean-schema/releases) or clone [this repo](https://github.com/intuit/lean-schema).

## Install the Project
```bash
cd lean-schema
make install
```

## Read and Edit the `codegen.properties` file
`codegen.properties` is used to control important things like:
- Where are your queries located?
- Where is your GraphQL Schema located?

### Set the `GRAPHQL_QUERIES_DIR` variable
Example: `GRAPHQL_QUERIES_DIR=/home/$YOU/proj/qb-mobile-graphql`

### Set the `GRAPHQL_SCHEMA_FILE` variable
Example: `GRAPHQL_SCHEMA_FILE=/home/$YOU/proj/graphql.json`

**Please Note**! LeanSchema currently understands [GraphQL Introspection Format](https://blog.apollographql.com/three-ways-to-represent-your-graphql-schema-a41f4175100d) Schemas. Please see the linked article for how to convert SDL and GraphQLSchemaObject Schemas to the Introsepction Format.

### Set the `COPY_UNMATCHED_FILES_DIR` variable

Like it says in the file, this controls where generated code files
that can't be matched by filename end up.

Example: Swift code generation creates a file called
`Types.swift`. Where does this file go after codegen? If
COPY_UNMATCHED_FILES_DIR is properly set, then it will be copied to
$COPY_UNMATCHED_FILES_DIR/Types.swift.

## Run the Code Generation
```bash
make codegen
```

## Build Artifacts
The generated code is located in `./codegen`. If
`COPY_GENERATED_FILES_AFTER_CODEGEN=true`, then all the generated
files are copied to $GRAPHQL_QUERIES_DIR by matching filenames.

Example:
```
│   ├── updateTripRule.graphql # This is a query
│   ├── updateTripRule.graphql.swift # This is the matching Swift file
│   ├── updateVehicle.graphql # This is a query
│   └── updateVehicle.graphql.swift # This is the matching Swift file
├── package.json
├── README.md
├── updateCompanyInfoFromSettings.graphql # This is a query
└── updateCompanyInfoFromSettings.graphql.swift # This is the matching Swift file
```

## Clean-up ie Reset the Project
```bash
make clean
```

# Extra Options
## Missing Types
LeanSchema is fairly aggresive in how many Types it prunes from the Schema. If you notice certain Types or Domains-of-Types are missing in the `lean_schema.json` file, you have these options:

## Increase the INPUT_OBJECT_DEPTH_LEVEL variable
In `./codegen.properties`:
```
# Default value is zero
INPUT_OBJECT_DEPTH_LEVEL=0
```
Increasing INPUT_OBJECT_DEPTH_LEVEL "unfolds" GraphQL InputObject Types. Example: your Queries include the `CreateSales_SaleInput` Type, which references the `Sales_SaleInput` Type. 
- If `INPUT_OBJECT_DEPTH_LEVEL=0`, only `CreateSales_SaleInput` is included.
- Else if `INPUT_OBJECT_DEPTH_LEVEL=1`, both `CreateSales_SaleInput` and `Sales_SaleInput` are included
- Else if `INPUT_OBJECT_DEPTH_LEVEL=2`, then **everything** that `Sales_SaleInput` references is included as well.

INPUT_OBJECT_DEPTH_LEVEL affects all of your InputObjects. These are Types that are typicaly used by Mutation Queries.

## Specify Types/Domains in types.yaml
The `./types.yaml` file is an optional file to specify which Types and Domains-of-Types you want to include in `lean_schema.json`. Example:
```yaml
# We want the following Schema Types
types:
  # We want everything that CreateSales_SaleInput references, in addition to CreateSales_SaleInput itself
  - "CreateSales_SaleInput":
      depth: 1
  # We just want Network_Contact and Entity
  - "Network_Contact"
  - "Entity"
  
# We want everything in the "risk" Domain at depth=0
domains:
  - "risk"
```

`types.yaml` lets you exactly state "trees-of-Types" to include in `lean_schema.json` by stating the root Types. Currently, Domains-of-Types are only included at depth=0. In the above example, everything under `risk` is included but **not** their direct references unless those types are found in your Queries.

# Questions & Answers

## When do I need to run `make install`?
On initial project setup and if a new version of the tool is released.

## When do I need to run `make codegen`?
When your GraphQL queries or GraphQL Schema change.

## How do I edit the Apollo command for Codegen?
If you need to change the Apollo commands, just change the `codegen` rule in the `makefile`:
```makefile
apollo client:codegen --passthroughCustomScalars --localSchemaFile=lean_schema.json --queries="queries/**/*.graphql" --target=swift codegen/
```

## Turn off the file copy & match for generated files?
Set `COPY_GENERATED_FILES_AFTER_CODEGEN=false` in `codegen.properties`

## Generate a single large file for codegen?
Change the `codegen` makefile command to this:
```makefile
apollo client:codegen --passthroughCustomScalars --localSchemaFile=lean_schema.json --queries="queries/**/*.graphql" --target=swift codegen.lean.swift
```
Only a single file named `codegen.lean.swift` will be created.
