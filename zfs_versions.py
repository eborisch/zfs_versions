#!/usr/bin/env python
# EAB 2016

"A little toy to find all saved (ZFS) versions of a file or directory."

from __future__ import print_function

import re
import sys

from os import path
from subprocess import check_output, call, check_call, STDOUT

if sys.platform[:5] == 'linux':
    LS = 'ls -ltr --time-style=full-iso'
elif sys.platform == 'sunos5':
    LS = '/usr/bin/ls -ltrE'
else:
    LS = 'ls -Tltr'

# If we have colordiff, use it for diff commands
try:
    check_call(('colordiff', '-v'), stdin=open('/dev/null', 'r'),
               stdout=open('/dev/null', 'w'), stderr=STDOUT)
    DIFF = 'colordiff'
except OSError as e:
    DIFF = 'diff'


def find_versions(path_in, print_mode=False):
    """
    Locate all zfs-snapshotted versions of path_in. Listed in time-order, with
    only updated versions listed (with the exception of the current file,
    which is always listed.)
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

    output = check_output('{0} {1} "{2}"/snapshot/*/"{3}"'.format(LS,
                                                                  ls_opts,
                                                                  zfs_dir,
                                                                  branch),
                          shell=True,
                          universal_newlines=True).split('\n')

    files = []

    if print_mode is True:
        sortable = re.compile('(.*zfs-auto-snap)_[a-z]+-([0-9h-]+)')
        sort_lines = []
        sort_last = None
        for line in output:
            if len(line) == 0:
                continue
            # This is to attempts to sort auto-snapshot names of identical
            # versions chronologically. Won't work for custom snapshot names
            # as we don't have direct access to their (snapshot) creation
            # times.
            files.append(line[line.find('/'):])
            found = sortable.search(line)
            if found:
                if found.group(1) != sort_last:
                    for l in sorted(sort_lines):
                        print(l[1])
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
                if print_mode is not None:
                    print(line)
                last = this

    # List the current (live on the filesystem) version.
    if path.exists('/'.join(orig)):
        # Don't call if the user is searching for a deleted file.
        if print_mode is not None:
            call('{0} {1} "{2}"'.format(LS, ls_opts, '/'.join(orig)),
                 shell=True)
        files.append('/'.join(orig))
    return files


def usage():
    print("Usage: zfs_versions.py [-a|--all] [--diff|--idiff] \n"
          "                       <path> [<path> ...]\n"
          "  -a|--all   Print all versions (not just changed.)\n"
          "  --diff     Show difference between history and current.\n"
          "  --idiff    Show incremental differences.\n"
          "  -r|--recursive  Recursive diffs on directories.")


if __name__ == "__main__":
    print_all = False
    diff = 0
    FLAGS = '-u'

    # Poor man's argparse to enable 2.6 compat.
    while len(sys.argv) > 1 and sys.argv[1][0] is '-':
        if sys.argv[1] in ('-a', '--all'):
            print_all = True
        elif sys.argv[1] == '--diff':
            diff = 1
            print_all = None
        elif sys.argv[1] == '--idiff':
            diff = 2
            print_all = None
        elif sys.argv[1] in ('-r', '--recursive'):
            FLAGS = FLAGS + 'r'
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
            print("*" * 78)
        vers = find_versions(p, print_all)
        if path.isdir(vers[-1]):
            # Don't echo back all the unchanged files.
            f = FLAGS
        else:
            f = FLAGS + 's'

        if diff == 1:
            for n in vers[:-1]:
                print("-"*78)
                sys.stdout.flush()
                call((DIFF, f, n, vers[-1]))
        elif diff == 2:
            for n in range(len(vers)-1):
                print("-"*78)
                sys.stdout.flush()
                call((DIFF, f, vers[n], vers[n+1]))
        sep = True

# vim: ts=4:sw=4:et:si:ai:
