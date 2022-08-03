#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile

import util

def launch_disp(sourcedir, passphrase, checksum_out):
	tarbytes = subprocess.check_output(["tar", "-C", sourcedir, "-c", "--bzip2", "-f", "-", "."])

	print("Packing tarball for qubes transfer")

	cmd = "~/permafrost/pfrecover.py --input --tar-stdin --checksum"
	if not passphrase.isalnum() or len(passphrase) < 8 or len(passphrase) > 256:
		print("Invalid passphrase", file=sys.stderr)
		sys.exit(1)
	input_bytes = passphrase.encode() + b"\n" + tarbytes

	print("Produced %d bytes, of which %d is the tarball" % (len(input_bytes), len(tarbytes)))
	print("Running unpack and checksum process")

	checksums = subprocess.check_output(["qvm-run-vm", "@dispvm", cmd], input=input_bytes).decode().split("\n")
	checksums = [line for line in checksums if line.strip()]
	if checksums[0] != "===== checksums =====" or checksums[-1] != "===== checksums =====" or checksums.count("===== checksums =====") != 2:
		print("Invalid output! Not just checksums.", file=sys.stderr)

		errpath = checksum_out + ".err"
		with open(errpath, "w") as f:
			for line in checksums:
				f.write(line + "\n")

		print("Written error data to path %s", errpath, file=sys.stderr)

		sys.exit(1)

	print("Decoding checksums...")

	with open(checksum_out, "w") as f:
		for line in checksums[1:-1]:
			f.write(line + "\n")

	print("Done!")

def dispatch(backup_vm, checksum_out):
	source_dir = os.path.join(util.UNSTAGING_PATH, backup_vm)

	if os.path.exists(checksum_out):
		print("Output path already exists", file=sys.stderr)
		sys.exit(1)

	passphrases = util.load_secret(".permafrostkeyring", use_json=True)
	if backup_vm not in passphrases or type(passphrases[backup_vm]) != str:
		print("Cannot find passphrase for", backup_vm, file=sys.stderr)
		sys.exit(1)

	launch_disp(source_dir, passphrases[backup_vm], checksum_out)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("usage: %s <backup-vm-name> <sha256sum.out>" % sys.argv[0], file=sys.stderr)
		sys.exit(1)
	dispatch(sys.argv[1], sys.argv[2])

