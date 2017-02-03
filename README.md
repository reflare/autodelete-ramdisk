# autodelete-ramdisk
A Linux-based solution allowing temporary files to exist for a few seconds before being disposed. Orders of magnitude faster than rm -rf.

#### Problem
In extreme use-cases such as fuzzing with several dozen cores, temporary files may be created faster than rm -rf can delete them.
This is due to the fact that rm -rf needs to manually enumerate files before unlinking them.

#### solution
By mounting two separate ramdisks and pointing a rotating symlink to one of them, we can unmount and remount the unused disk after a cool-down phase. This allows files to be written and persist for seconds or much longer (depending on the rotation speed) before being deleted. Unmounting a ramdisk destroys all files stored on it instantly without needing to enumerate them.

#### Usage
`./autodelete-ramdisk.py symlink mountpoint_a mountpoint_b size_in_mb rotation_time`

#### Options
`symlink` The symlink pointing to the currently active ramdisk.
`mountpoint_a` Mountpoint for the first ramdisk.
`mountpoint_b` Mountpoint for the second ramdisk.
`size_in_mb` Size of each ramdisk in MB.
`rotation_time` Switch between ramdisks every X seconds.

#### Important
Never write files you wish to keep to either of the ramdisks. The system is designed to be non-persistent.
Always write files to the symlink, not to the ramdisks directly.

#### Installation

Place afl-monitor anywhere in your file system and execute it. Requires Python 2.7.
