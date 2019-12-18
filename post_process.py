#! /usr/bin/env python

"""
Post processing for Lean Schema Codegen. Does stuff like:
- Copy/match codegen files to the source queries directory

"""

__author__ = 'prussell'

import argparse
import os
import shutil

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir", help="The source directory of the generated codegen files")
    parser.add_argument("dst_dir", help="The destination directory to copy the generated codegen files to")
    parser.add_argument("--copy-codegen-files", help="Copy generated code files to some destination directory and attempt to match by query filenames", choices=("true", "True", "False", "false", True, False), default=True)
    parser.add_argument("--src-files-extension", help="The extension of the codegen sourcefiles", default="swift")
    parser.add_argument("--debug", action='store_true', help="Turn on debugging info")
    parser.add_argument("--copy-unmatched-files-dir", help="Directory to copy unmatched code-generated files to", default=None)

    args = parser.parse_args()

    if args.copy_codegen_files not in {True, "true", "True"}:
        print("--copy-codegen-files is not set to True: {}".format(args.copy_codegen_files))
        exit(0)

    # Error checking
    src_dir = os.path.abspath(args.src_dir)
    if not (os.path.exists(src_dir) and os.path.isdir(src_dir)):
        print("src_dir {} does not exist!".format(src_dir))
        exit(1)

    dst_dir = os.path.abspath(args.dst_dir)
    if not (os.path.exists(dst_dir) and os.path.isdir(dst_dir)):
        print("dst_dir {} does not exist!".format(dst_dir))
        exit(1)

    if args.copy_unmatched_files_dir is not None:
        copy_unmatched_files_dir = os.path.abspath(args.copy_unmatched_files_dir)
        if not (os.path.exists(copy_unmatched_files_dir)
                and
                os.path.isdir(copy_unmatched_files_dir)):
            print("copy-unmatched-files-dir {} does not exist!".format(copy_unmatched_files_dir))
            exit(1)
    else:
        copy_unmatched_files_dir = None

    # Get all codegen filenames and store as a dict. Apollo (currently) dumps them out as a flat directory
    files_table = {filename.split(".")[0] : {"src" : os.path.join(os.path.abspath(src_dir),
                                                                  filename),
                                             "dst" : copy_unmatched_files_dir}
                   for filename in os.listdir(src_dir)
                   if filename.endswith(args.src_files_extension)}

    # Trawl through the dst tree and match by file prefix to find the dest file-path
    for root, dirs, files in os.walk(dst_dir):
        for fname in files:
            key = fname.split(".")[0]
            if key in files_table:
                files_table[key]["dst"] = os.path.join(root, fname)

    # We now have a complete mapping of src->dst, just copy everything
    for value in files_table.values():
        src = value['src']
        dst = value['dst']
        if dst is None:
            print("Error: codegen file {} does not have a match in dst?".format(src))
            continue

        if not os.path.isdir(dst):
            dst_dir = os.path.split(os.path.abspath(dst))[0]
        else:
            dst_dir = dst

        src_fname = os.path.split(src)[1]
        dst_fname = os.path.join(dst_dir, src_fname)
        if args.debug:
            print("Copying {} to {}".format(src, dst_fname))
        shutil.copyfile(src, dst_fname)

    # That's it
