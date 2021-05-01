#!/usr/bin/env python3
import os
import subprocess
import sys

import util

def msg(*text):
	print(*text, file=sys.stderr)
	sys.stderr.flush()

def duplicity_restore(source, dest, passphrase):
	msg("performing duplicity restore")
	nenv = dict(os.environ)
	nenv["PASSPHRASE"] = passphrase
	subprocess.check_call(["duplicity", "restore", "--progress", "--", "file://" + os.path.abspath(source), os.path.abspath(dest)], env=nenv, stdout=sys.stderr, stderr=sys.stderr)

PASSFILE="/home/user/.permafrostkey"
TARGET="/home/user/Materials"
SOURCE_VM="permathaw"
READ_SOURCE="/home/user/QubesIncoming/" + SOURCE_VM
TAR_SOURCE="/home/user/TarUnpack/"
TAR_TEMP="/home/user/unpack-tarball.tar.bz2"

input_tar = False
input_passphrase = False
do_checksum = False

def pull_tarball():
	total = 0
	with open(TAR_TEMP, "wb") as f:
		while True:
			data = sys.stdin.buffer.read(64 * 1024)
			if not data: break
			total += len(data)
			f.write(data)
	return total

def backup():
	source = READ_SOURCE
	if input_passphrase:
		msg("Passphrase?")
		passphrase = sys.stdin.buffer.readline().strip().decode()
		if not passphrase.isalnum():
			msg("Not a valid passphrase")
			sys.exit(1)
		if input_tar:
			msg("Reading tarball from stdin...")
			count = pull_tarball()
			msg("Unpacking tarball (%d bytes)..." % count)
			subprocess.check_call(["tar", "-C", TAR_SOURCE, "-x", "--bzip2", "-f", TAR_TEMP], stdout=sys.stderr, stderr=sys.stderr)
			source = TAR_SOURCE
			msg("Unpacked!")
	else:
		assert not input_tar, "not supported yet: --tar-stdin without --input"
		with open(PASSFILE, "r") as f:
			passphrase = f.read().strip()
	msg("beginning...")
	try:
		duplicity_restore(source, TARGET, passphrase)
	except Exception as e:
		raise e
	msg("finished restore!")
	if do_checksum:
		print("===== checksums =====")
		sys.stdout.flush()
		subprocess.check_call(["find", "-type", "f", "-exec", "sha256sum", "{}", ";"], cwd=TARGET)
		print("===== checksums =====")
		sys.stdout.flush()

if __name__ == "__main__":
	for flag in sys.argv[1:]:
		if flag == "--input":
			input_passphrase = True
		elif flag == "--tar-stdin":
			input_tar = True
		elif flag == "--checksum":
			do_checksum = True
		else:
			msg("Unexpected flag: %r" % flag)
			sys.exit(1)
	backup()
