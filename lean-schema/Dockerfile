# Dockerfile for the Schema Decomposition/Lean Schema tool
# @author: prussell

# Node stuff
# Tested with 10.12.0, but any 10.x version is fine
FROM node:10
WORKDIR /opt/intuit/pte/leanschema
RUN apt-get -y update && apt-get -y upgrade
COPY get_types_for_queries.js .
RUN npm install apollo@1.9.2
RUN npm install typescript
# Find node modules starting at...
ENV NODE_PATH "./"
# Add Apollo command to PATH
ENV PATH="/opt/intuit/pte/leanschema/node_modules/.bin:${PATH}"

# Python stuff
COPY decomp.py .
COPY requirements.txt .
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install python3-pip
RUN pip3 install -r requirements.txt

# Use the makefile to actually run commands
COPY build.makefile ./makefile
COPY codegen.properties .