#!/usr/bin/env python3
import os

import util

def check_incoming(source, dest):
	print("checking incoming files...")
	errors = []
	counts = {}
	for svm in os.listdir(source):
		svmpath = os.path.join(source, svm)
		dvmpath = os.path.join(dest, svm)
		count, octets = 0, 0
		for f in os.listdir(svmpath):
			fpath = os.path.join(svmpath, f)
			dpath = os.path.join(dvmpath, f)
			if os.path.isdir(fpath):
				errors.append("skipping directory %s" % repr(fpath))
				continue
			if os.path.exists(dpath):
				errors.append("skipping duplicate file %s" % repr(fpath))
				continue
			size = os.stat(fpath).st_size
			if size == 0:
				errors.append("skipping zero-sized file %s" % repr(fpath))
				continue
			if not os.path.isdir(os.path.dirname(dpath)):
				os.makedirs(os.path.dirname(dpath))
			os.rename(fpath, dpath)
			count += 1
			octets += size
		if not count:
			continue
		counts[svm] = (count, octets)
	return errors, counts

def main():
	notify = util.Notifier()
	errors, counts = check_incoming("/home/user/QubesIncoming", util.STAGING_PATH)
	lines = []
	if errors:
		lines += ["encountered %d errors:" % len(errors)]
		for err in errors:
			lines += [" * %s" % err]
	if counts:
		tcount = sum(count for count, size in counts.values())
		tsize = sum(size for count, size in counts.values())
		lines += ["accepted %d files from %d VMs (%s)" % (tcount, len(counts), util.sizeof_fmt(tsize))]
		for vm, (count, size) in sorted(counts.items()):
			lines += [" * %s: %d (%s)" % (repr(vm), count, util.sizeof_fmt(tsize))]
	if lines:
		notify.send("\n".join(lines))

if __name__ == "__main__":
	main()
