#! /usr/bin/python
#
# A Linux-based solution allowing temporary files to exist for a few seconds
# before being disposed. Orders of magnitude faster than rm -rf.
# -------------------------------------------------
#
# Written and maintained by Paul S. Ziegler
#
# Copyright 2017 Reflare Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http://www.apache.org/licenses/LICENSE-2.0
#

from sys import argv,exit
from os import path, system
from commands import getstatusoutput
from time import sleep
import signal

def printUsage():
    print """Usage: ./autodelete-ramdisk.py symlink mountpoint_a mountpoint_b size_in_mb rotation_time
symlink:\tThe symlink pointing to the currently active ramdisk.
mountpoint_a:\tMountpoint for the first ramdisk.
mountpoint_b:\tMountpoint for the second ramdisk.
size_in_mb:\tSize of each ramdisk in MB.
rotation_time:\tSwitch between ramdisks every X seconds.
"""

if len(argv) != 6:
    printUsage()
    exit()

SYMLINK = argv[1]
MOUNTPOINT_A = argv[2]
MOUNTPOINT_B = argv[3]
SIZE = argv[4]
ROTATIONTIME = argv[5]

# Sanity checks
if path.isdir(SYMLINK) or path.isfile(SYMLINK):
    print "[ERROR] Symlink exists. Please specify a non-existing path for the symlink."
    exit()

if not path.isdir(MOUNTPOINT_A):
    print "[ERROR] Mountpoint A does not exist."
    exit()

if not path.isdir(MOUNTPOINT_B):
    print "[ERROR] Mountpoint B does not exist."
    exit()

try:
    SIZE = int(SIZE)
except:
    print "[ERROR] Invalid size_in_mb."
    exit()

if SIZE <= 0:
    print "[ERROR] Invalid size_in_mb."
    exit()

try:
    ROTATIONTIME = int(ROTATIONTIME)
except:
    print "[ERROR] Invalid rotation_time."
    exit()

if ROTATIONTIME <= 0:
    print "[ERROR] Invalid rotation_time."
    exit()

def cleanup():
    system("fuser -km %s" % MOUNTPOINT_A)
    system("umount -f %s" % MOUNTPOINT_A)
    system("fuser -km %s" % MOUNTPOINT_B)
    system("umount -f %s" % MOUNTPOINT_B)
    system("rm -f %s" % SYMLINK)
    exit()

# Mount both disks
if getstatusoutput("mount -t tmpfs -o size=%dm tmpfs %s" % (SIZE, MOUNTPOINT_A))[0] != 0:
    print "[ERROR] Somethign went wrong while mounting ramdisk A."
    cleanup()
if getstatusoutput("mount -t tmpfs -o size=%dm tmpfs %s" % (SIZE, MOUNTPOINT_B))[0] != 0:
    print "[ERROR] Somethign went wrong while mounting ramdisk B."
    cleanup()

# Create symlink
if getstatusoutput("ln -s -f -n %s %s" % (MOUNTPOINT_A, SYMLINK))[0] != 0:
    print "[ERROR] Couldn't create symlink."
    cleanup()

def signal_handler(signal, frame):
    cleanup()
signal.signal(signal.SIGINT, signal_handler)

HALFTIME = ROTATIONTIME / 2.0

print "Initialization complete. Will rotate disks every %d seconds and clean unused disk after %.2f seconds." % (ROTATIONTIME, HALFTIME)
CLEANDISK = MOUNTPOINT_B
ACTIVEDISK = MOUNTPOINT_A
while True:
    sleep(HALFTIME)
    print "Cleaning %s..." % CLEANDISK
    system("fuser -km %s" % CLEANDISK)
    system("umount -f %s" % CLEANDISK)
    system("mount -t tmpfs -o size=%dm tmpfs %s" % (SIZE,CLEANDISK))
    sleep(HALFTIME)
    print "Switching disks to %s" % CLEANDISK
    system("ln -s -f -n %s %s" % (CLEANDISK, SYMLINK))
    TMPDISK = CLEANDISK
    CLEANDISK = ACTIVEDISK
    ACTIVEDISK = TMPDISK
