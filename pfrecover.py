#!/usr/bin/env python3
import os
import subprocess
import sys

import util

def duplicity_restore(source, dest, passphrase):
	print("performing duplicity restore")
	nenv = dict(os.environ)
	nenv["PASSPHRASE"] = passphrase
	subprocess.check_call(["duplicity", "restore", "--progress", "--", "file://" + os.path.abspath(source), os.path.abspath(dest)], env=nenv)

PASSFILE="/home/user/.permafrostkey"
TARGET="/home/user/Materials"
SOURCE_VM="permathaw"
READ_SOURCE="/home/user/QubesIncoming/" + SOURCE_VM

input_passphrase = False
do_checksum = False

def backup():
	if input_passphrase:
		passphrase = input("Passphrase> ")
	else:
		with open(PASSFILE, "r") as f:
			passphrase = f.read().strip()
	print("beginning...")
	try:
		duplicity_restore(READ_SOURCE, TARGET, passphrase)
	except Exception as e:
		raise e
	print("finished restore!")
	if do_checksum:
		print("===== checksums =====")
		subprocess.check_call(["find", "-type", "f", "-exec", "sha256sum", "{}", ";"], cwd=TARGET)
		print("===== checksums =====")

if __name__ == "__main__":
	for flag in sys.argv[1:]:
		if flag == "--input":
			input_passphrase = True
		elif flag == "--checksum":
			do_checksum = True
		else:
			print("Unexpected flag: %r" % flag)
			sys.exit(1)
	backup()
