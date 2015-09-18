#!/usr/bin/python
# Copyright MacTechs, 2014. All rights reserved.
# Intended for use with Mac OS 10.10.4 


import os
import plistlib
import subprocess
import sys
import uuid

# Returns path to plist if it exists, None otherwise.
def getPlist(plist):
	user_home = os.path.expanduser('~')
	print "searching %s for %s" % (user_home, plist)
	for root, dirs, files in os.walk(user_home):
		if plist in files:
			path = os.path.join(root, plist)
			print "found: %s" % path
			return path
	print "Plist not found in user home directory."
	return None

# Returns dict containing information read from plist file.
# Converts plist to xml1 form before reading if it is a binary plist.
def readPlist(plist_path):
	print "Reading %s into dict" % (plist_path)
	try:
		pl = plistlib.readPlist(plist_path)
	except:
		print "Plist appears to be in binary form, converting to xml"
		subprocess.call(['plutil', '-convert', 'xml1', plist_path])
		pl = plistlib.readPlist(plist_path)
	return pl

# Adds a bookmark to the plist dictionary.
def addBookmark(plist, name, url):
	uri_dict = dict(
		title=name
	)
	bookmark = dict(
		WebBookmarkType='WebBookmarkTypeLeaf',
		WebBookmarkUUID=str(uuid.uuid5(uuid.NAMESPACE_DNS, name)),
		URLString=url,
		URIDictionary=uri_dict,
	)
	plist['Children'][1]['Children'].append(bookmark)

# Removes a bookmark from the plist dictionary.
def removeBookmark(plist):
	pass

# Writes plist to specified path.
# Converts to binary form after writing if binary=True.
def writePlist(plist, plist_path, binary=False):
	print "Writing modified plist to %s" % (plist_path)
	plistlib.writePlist(plist, plist_path)
	if binary:
		print "Converting %s to binary." % (plist_path)
		subprocess.call(['plutil', '-convert', 'binary1', plist_path])
	print "Done"

def main():
	to_add = {"Nfl.com": "http://www.nfl.com", "reddit": "http://www.reddit.com"}
	plist_path = getPlist('Bookmarks.plist')
	if plist_path is None:
		sys.exit(1)
	plist = readPlist(plist_path)
	for name, url in to_add.iteritems():
		addBookmark(plist, name, url)
	print plist
	writePlist(plist, plist_path, binary=True)


if __name__ == "__main__":
    main()
