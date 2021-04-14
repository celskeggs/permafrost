#!/usr/bin/env python3
import os
import sys

import dbm.gnu

import util

UNSTAGE_INDEXES="/home/user/unstaging-indexes"

def dispatch(backup_vm, restore_vm):
	source_dir = os.path.join(util.UNSTAGING_PATH, backup_vm)
	index_path = os.path.join(UNSTAGE_INDEXES, restore_vm)
	print("beginning...")
	with dbm.gnu.open(index_path, "cs") as db:
		for f in os.listdir(source_dir):
			fpath = os.path.join(source_dir, f)
			if f not in db:
				try:
					util.qvm_copy(fpath, restore_vm)
				except Exception as e:
					raise e
				db[f] = "ok"
	print("finished!")

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("usage: %s <backup-vm-name> <restore-vm-name>" % sys.argv[0], file=sys.stderr)
		sys.exit(1)
	dispatch(sys.argv[1], sys.argv[2])

