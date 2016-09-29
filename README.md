# zfs_versions
Python script for showing versions / diffs of a file in ZFS snapshots.

```
 Usage: zfs_versions.py [-a|--all] [--diff|--idiff]
                        <path> [<path> ...]
  -a|--all   Print all versions (not just changed.)
  --diff     Show difference between history and current.
  --idiff    Show incremental differences.
```

This does not use the ```zfs``` executable, and only relies on being able to enter and list .zfs/snapshot/foo directories. This allows it to work not only directly on **ZFS hosts**, but also on zfs-backed **NFS** or **netatalk** shares, as well as for **normal users on ZFS on Linux** -- where ```zfs``` (at least pre 0.7.0) required elevated permissions.

This is also designed to play nicely wih zfs-auto-snapshot, but does not rely on it for functionality.

Uses ```colordiff``` if it is in PATH for ```--diff``` and ```--idiff``` modes.

Example output; listing historical versions.
```
$ zfs_versions.py /etc/motd
-rw-r--r--  1 root  wheel  97 Sep 16 22:41:47 2015 /.zfs/snapshot/zfs-auto-snap_monthly-2015-10-01-00h28/etc/motd
-rw-r--r--  1 root  wheel  97 Oct 23 20:33:46 2015 /.zfs/snapshot/zfs-auto-snap_monthly-2015-11-01-00h28/etc/motd
-rw-r--r--  1 root  wheel  97 Nov 17 22:33:10 2015 /.zfs/snapshot/zfs-auto-snap_monthly-2015-12-01-00h28/etc/motd
-rw-r--r--  1 root  wheel  97 Dec  7 22:36:35 2015 /.zfs/snapshot/zfs-auto-snap_monthly-2016-01-01-00h28/etc/motd
-rw-r--r--  1 root  wheel  98 Jan 27 18:55:46 2016 /.zfs/snapshot/zfs-auto-snap_monthly-2016-02-01-00h28/etc/motd
-rw-r--r--  1 root  wheel  98 Feb 13 10:19:44 2016 /.zfs/snapshot/zfs-auto-snap_monthly-2016-03-01-00h28/etc/motd
-rw-r--r--  1 root  wheel  95 Mar 25 11:21:55 2016 /.zfs/snapshot/zfs-auto-snap_monthly-2016-05-01-00h28/etc/motd
-rw-r--r--  1 root  wheel  97 May 31 23:23:02 2016 /.zfs/snapshot/zfs-auto-snap_monthly-2016-08-01-00h28/etc/motd
-rw-r--r--  1 root  wheel  91 Aug 31 21:50:46 2016 /.zfs/snapshot/zfs-auto-snap_weekly-2016-09-11-00h14/etc/motd
-rw-r--r--  1 root  wheel  91 Sep 13 23:37:58 2016 /.zfs/snapshot/zfs-auto-snap_weekly-2016-09-18-00h14/etc/motd
-rw-r--r--  1 root  wheel  95 Sep 23 20:53:51 2016 /.zfs/snapshot/zfs-auto-snap_weekly-2016-09-25-00h14/etc/motd
-rw-r--r--  1 root  wheel  95 Sep 23 20:53:51 2016 /etc/motd
```

Incremental diff mode:

```
$ zfs_versions.py --idiff /etc/motd
------------------------------------------------------------------------------
--- /.zfs/snapshot/zfs-auto-snap_monthly-2015-10-01-00h28/etc/motd      2015-09-16 22:41:47.358861003 -0500
+++ /.zfs/snapshot/zfs-auto-snap_monthly-2015-11-01-00h28/etc/motd      2015-10-23 20:33:46.902232864 -0500
@@ -1,4 +1,4 @@
-FreeBSD 10.2-RELEASE-p3 (EABKERN) #1 r287891: Wed Sep 16 22:26:52 CDT 2015
+FreeBSD 10.2-RELEASE-p5 (EABKERN) #1 r289727: Wed Oct 21 21:10:23 CDT 2015

 Welcome to FreeBSD!

------------------------------------------------------------------------------
--- /.zfs/snapshot/zfs-auto-snap_monthly-2015-11-01-00h28/etc/motd      2015-10-23 20:33:46.902232864 -0500
+++ /.zfs/snapshot/zfs-auto-snap_monthly-2015-12-01-00h28/etc/motd      2015-11-17 22:33:10.787956414 -0600
@@ -1,4 +1,4 @@
-FreeBSD 10.2-RELEASE-p5 (EABKERN) #1 r289727: Wed Oct 21 21:10:23 CDT 2015
+FreeBSD 10.2-RELEASE-p7 (EABKERN) #4 r291009: Tue Nov 17 22:17:16 CST 2015

 Welcome to FreeBSD!

------------------------------------------------------------------------------
--- /.zfs/snapshot/zfs-auto-snap_monthly-2015-12-01-00h28/etc/motd      2015-11-17 22:33:10.787956414 -0600
+++ /.zfs/snapshot/zfs-auto-snap_monthly-2016-01-01-00h28/etc/motd      2015-12-07 22:36:35.874043640 -0600
@@ -1,4 +1,4 @@
-FreeBSD 10.2-RELEASE-p7 (EABKERN) #4 r291009: Tue Nov 17 22:17:16 CST 2015
+FreeBSD 10.2-RELEASE-p8 (EABKERN) #5 r291971: Mon Dec  7 22:19:30 CST 2015

 Welcome to FreeBSD!
 <-- snip -->
 ```
