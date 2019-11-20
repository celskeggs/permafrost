#!/usr/bin/env python3
import os
import subprocess
import dbm.gnu
import argparse

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

def qvm_copy(path, target_vm):
	print("copying file", path, "to vm", target_vm)
	nenv = dict(os.environ)
	nenv["PROGRESS_TYPE"] = "none"
	subprocess.check_call(["/usr/lib/qubes/qrexec-client-vm", target_vm, "qubes.Filecopy", "/usr/lib/qubes/qfile-agent", path], env=nenv)

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
		if db.get("state", b"idle") != b"idle":
			raise Exception("index not idle: %s" % db["state"])
		db["state"] = "active"
		try:
			duplicity_backup(TARGET, STAGING, passphrase)
		except Exception as e:
			db["state"] = "backup-failed"
			raise e
		for f in os.listdir(STAGING):
			fpath = os.path.join(STAGING, f)
			if f == "index" or f == "state":
				continue
			if f not in db:
				try:
					qvm_copy(fpath, TARGET_VM)
				except Exception as e:
					db["state"] = "copy-failed"
					raise e
				db[f] = "ok"
		db["state"] = "idle"
	print("finished!")

def recover():
	with dbm.gnu.open(STAGE_INDEX, "cs") as db:
		if db.get("state", "idle") == "idle":
			raise Exception("index already idle")
		db["state"] = "idle"
	print("recovered.")

def main():
	parser = argparse.ArgumentParser(description='Back up files.')
	parser.add_argument('--recover', action="store_true", help='reset state to idle')
	args = parser.parse_args()
	if args.recover:
		recover()
	else:
		backup()

if __name__ == "__main__":
	main()
