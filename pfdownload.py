#!/usr/bin/env python3
import os
import time

import requests

import util

def validate_path(path):
	# in particular, this safelist prevents "." or ".." or any absolute paths from being accepted
	for part in path.split("/"):
		for subpart in part.split("."):
			if not subpart or not subpart.replace("-","").isalnum():
				return False
	return True

assert validate_path("test/test-123.py")
assert not validate_path(".")
assert not validate_path("..")
assert not validate_path("test/../test")
assert not validate_path("abc/./def")
assert not validate_path("/test/test/..")
assert not validate_path("/test/abc")
assert validate_path("test/abc")

def download_all(local_path):
	if not os.path.isdir(local_path):
		raise Exception("nonexistent unstaging directory")
	bucket = util.connect_bucket()
	all_available = {obj.key: obj.size for obj in bucket.objects.all()}
	remaining = set(all_available.keys())
	for path, folders, files in os.walk(local_path):
		for f in files:
			lpath = os.path.join(path, f)
			rpath = os.path.relpath(lpath, local_path)
			local_size = os.stat(lpath).st_size
			if rpath not in remaining:
				raise RuntimeError("expected previously downloaded file %s of size %d to still exist remotely" % (rpath, local_size))
			if local_size != all_available[rpath]:
				raise Exception("expected previously downloaded file %s to be of size %d, not %d" % (rpath, all_available[rpath], local_size))
			remaining.remove(rpath)
	total_count, total_size = 0, 0
	for rpath in remaining:
		assert validate_path(rpath), "invalid path: %s" % repr(rpath)
		lpath = os.path.join(local_path, rpath)
		print("downloading", rpath, "to", lpath, "of size", util.sizeof_fmt(all_available[rpath]))
		if not os.path.isdir(os.path.dirname(lpath)):
			os.makedirs(os.path.dirname(lpath))
		bucket.download_file(rpath, lpath)
		local_size = os.stat(lpath).st_size
		if local_size != all_available[rpath]:
			raise Exception("expected newly downloaded file %s to be of size %d, not %d" % (rpath, all_available[rpath], local_size))
		total_count += 1
		total_size += local_size
	bucket_size = sum(all_available.values())
	return total_count, total_size, bucket_size

def main():
#	notify = util.Notifier()
	start_time = time.time()
	total_count, total_size, bucket_size = download_all(util.UNSTAGING_PATH)
	total_time = time.time() - start_time
	if total_count:
		print("downloaded %d files of total size %s in %f seconds; total bucket size is %s" % (total_count, util.sizeof_fmt(total_size), round(total_time, 1), util.sizeof_fmt(bucket_size)))
	else:
		print("nothing to do")

if __name__ == "__main__":
	main()

