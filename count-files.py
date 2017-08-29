#!/usr/bin/env python3

"""
usage: count-files [-d] [DIR]

Counts the number of files in DIR recursively, grouped by its subdirectories

options:
    -d  include directories as well; by default directories are not included
          in the final count so if you had a hierarcy like this:
              base/file1
              base/file2
              base/dir1
              base/dir1/file3
              base/dir1/dir2
              base/dir1/dir2/file4
          then base would be considered to have a count of 2 and dir1 of 2 as
          well; with this options, base and dir1 would both have 3
"""

import os
import sys
from collections import Counter

import docopt


def walk_err(exc):
    print("count-files: %s: %s" % (exc.filename, exc.strerror))
    sys.exit(1)


def main(basedir, count_dirs):
    # I also have an implementation in shellscript but surprisingly this python
    # rewrite is not that bigger with the extra benefit of not breaking in the
    # face of paths with newlines or being not portable / GNU-only.

    # TODO: Add an option to control the "depth" of the grouping?  Like,
    # consider the example for the -d options (and assume that it's on).  Then
    # depth == 0:
    #     6 base
    # depth == 1:
    #     3 dir1
    #     3 base
    # depth == 2:
    #     1 dir1/dir2
    #     2 dir1
    #     3 base
    # In this example any other value for depth would produce the same result.

    counts: Counter = Counter()

    for root, dirs, files in os.walk(basedir, onerror=walk_err):
        base_rel = os.path.relpath(root, start=basedir)
        base_subdir = base_rel.split(os.path.sep, 1)[0]
        counts[base_subdir] += len(files)
        if count_dirs:
            counts[base_subdir] += len(dirs)

    max_count_len = max(len(str(c)) for c in counts.values())
    for name, count in reversed(counts.most_common()):
        print(" %*d %s" % (max_count_len, count, name))


if __name__ == "__main__":
    opts = docopt.docopt(__doc__, sys.argv[1:])
    basedir = opts["DIR"] or "."
    count_dirs = opts["-d"]
    main(basedir, count_dirs)
