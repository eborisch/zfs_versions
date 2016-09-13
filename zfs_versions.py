#!/usr/bin/env python
# EAB 2016

"A little toy to find all saved (ZFS) versions of a file or directory."

from __future__ import print_function

import re
import sys

from operator import itemgetter
from os import path
from subprocess import check_output, call

if sys.platform[:5] == 'linux':
    LS_CMD = 'ls -ltr --time-style=full-iso'
else:
    LS_CMD = 'ls -Tltr'


def find_versions(path_in, print_all=False):
    """
    Locate all zfs-snapshotted versions of path_in. Listed in time-order, with
    only updated versions listed (with the exception of the current file, which
    is always listed.)
    """
    ls_opts = '-d' if path.isdir(path_in) else ''
    orig = path.abspath(path_in).split('/')

    zfs_point = len(orig)

    while zfs_point > 0:
        zfs_dir = '/'.join(orig[:zfs_point]) + '/.zfs'
        if path.isdir(zfs_dir):
            break
        else:
            zfs_point = zfs_point - 1

    if zfs_point == 0:
        raise IOError("Unable to find .zfs directory. "
                      "Is [{0}] on a ZFS filesystem?".format(path_in))

    branch = '/'.join(orig[zfs_point:])

    output = check_output('{0} {1} "{2}"/snapshot/*/"{3}"'.format(LS_CMD,
                                                                  ls_opts,
                                                                  zfs_dir,
                                                                  branch),
                          shell=True,
                          universal_newlines=True).split('\n')

    files = []

    if print_all:
        sortable = re.compile('(.*zfs-auto-snap)_[a-z]+-([0-9h-]+)')
        sort_lines = []
        sort_last = None
        for line in output:
            if len(line) == 0:
                continue
            # This is to attempts to sort auto-snapshot names of identical
            # versions chronologically. Won't work for custom snapshot names as
            # we don't have direct access to their (snapshot) creation times.
            files.append(line[line.find('/'):])
            found = sortable.search(line)
            if found:
                if found.group(1) != sort_last:
                    for l in sorted(sort_lines):
                        print( l[1])
                    sort_lines[:] = []
                    sort_last = found.group(1)
                sort_lines.append((found.group(2), line))
            else:
                # Put custom snapshots at bottom of identical version list
                sort_lines.append(('9', line))
        for l in sorted(sort_lines):
            # Required to print off the last batch collected in sort_lines
            print(l[1])
    else:   # Only print changes
        last = None
        for line in output:
            if len(line) == 0:
                continue
            this = line[:line.find('/')]
            if this != last:
                files.append(line[line.find('/'):])
                print(line)
                last = this

    # List the current (live on the filesystem) version.
    if path.exists('/'.join(orig)):
        # Don't call if the user is searching for a deleted file.
        call('{0} {1} "{2}"'.format(LS_CMD, ls_opts, '/'.join(orig)),
             shell=True)
        files.append('/'.join(orig))
    return files

def usage():
    print("Usage: zfs_versions.py [-a|--all] [--diff|--idiff] \n"
          "                       <path> [<path> ...]\n"
          "  -a|--all   Print all versions (not just changed.)\n"
          "  --diff     Show difference between current and history.\n"
          "  --idiff    Show incremental differences.")


if __name__ == "__main__":
    filt = False
    diff = 0

    # Poor man's argparse to enable 2.6 compat.
    while len(sys.argv) > 1 and sys.argv[1][0] is '-':
        if sys.argv[1] in ('-a', '--all'):
            filt = True
        elif sys.argv[1] == '--diff':
            diff = 1
        elif sys.argv[1] == '--idiff':
            diff = 2
        else:
            usage()
            print("")
            print("Unrecognized option: {0}".format(sys.argv[1]))
            sys.exit(1)
        sys.argv.pop(1)

    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    sep = False
    for p in sys.argv[1:]:
        if sep:
            print("==")
        vers = find_versions(p, filt)
        if diff == 1:
            for n in vers[:-1]:
                print("-"*78)
                call(('diff', '-su', n, vers[-1]))
        elif diff == 2:
            for n in range(len(vers)-1):
                print("-"*78)
                call(('diff', '-su', vers[n], vers[n+1]))


        sep = True

# vim: ts=4:sw=4:et:si:ai:
