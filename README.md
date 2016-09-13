# zfs_versions
Python script for showing versions / diffs of a file in ZFS snapshots.

```
 Usage: zfs_versions.py [-a|--all] [--diff|--idiff]
                        <path> [<path> ...]
  -a|--all   Print all versions (not just changed.)
  --diff     Show difference between current and history.
  --idiff    Show incremental differences.
```
