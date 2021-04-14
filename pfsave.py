#!/usr/bin/env python3
import argparse
import os
import subprocess

import dbm.gnu

import util

def duplicity_backup(source, dest, passphrase):
	print("performing duplicity backup")
	nenv = dict(os.environ)
	nenv["PASSPHRASE"] = passphrase
	args = ["--progress", "--", os.path.abspath(source), "file://" + os.path.abspath(dest)]
	delta = [int(ent.split(b" ",1)[1]) for ent in subprocess.check_output(["duplicity", "--dry-run"] + args, env=nenv).split(b"\n") if ent.startswith(b"DeltaEntries")]
	if len(delta) != 1:
		raise Exception("invalid --dry-run output format")
	delta, = delta
	if not delta:
		print("no changes to backup")
		return
	subprocess.check_call(["duplicity"] + args, env=nenv)

PASSFILE="/home/user/.permafrostkey"
TARGET="/home/user/Materials"
STAGING="/home/user/bkstage"
STAGE_INDEX="/home/user/bkstage/index"
TARGET_VM="permafrost"

def backup():
	with open(PASSFILE, "r") as f:
		passphrase = f.read().strip()
	print("beginning...")
	with dbm.gnu.open(STAGE_INDEX, "cs") as db:
		try:
			duplicity_backup(TARGET, STAGING, passphrase)
		except Exception as e:
			raise e
		for f in os.listdir(STAGING):
			fpath = os.path.join(STAGING, f)
			if f == "index":
				continue
			if f not in db:
				try:
					util.qvm_copy(fpath, TARGET_VM)
				except Exception as e:
					raise e
				db[f] = "ok"
	print("finished!")

if __name__ == "__main__":
	backup()
