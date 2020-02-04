#!/usr/bin/env python3

import sys
import json
import os

def main(args):
    if not len(args) == 1:
        usage()
        sys.exit(1)

    abs_path = os.path.abspath(args[0])
    if not (os.path.exists(abs_path) and os.path.isfile(abs_path)):
        print("schema_file must be a file", file=sys.stderr)
        sys.exit(1)

    if not is_file_good(abs_path):
        print("You must have a valid schema_file. If you only have SDL, you may use the convert.js script, which requires node.", file=sys.stderr)
        sys.exit(2)

"""
Check if the schema file is good for our purposes.
Basically, this boils down to if it is valid json with either:
  .data.__schema
  or
  .__schema
"""
def is_file_good(file_path):

    # open file and read as JSON
    with open(file_path) as f:
        try:
            contents = json.load(f)
        except:
            return False

    # check the .__schema case
    if '__schema' in contents:
        return True
    # check the .data.__schema case
    elif 'data' in contents and '__schema' in contents['data']:
        return True
    else:
        return False

def usage():
    print("Usage: {} schema_file".format(sys.argv[0]), file=sys.stderr)

if __name__ == '__main__':
    main(sys.argv[1:])
