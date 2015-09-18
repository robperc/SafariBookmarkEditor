#!/usr/bin/python
# Copyright MacTechs, 2014. All rights reserved.
# Intended for use with Mac OS 10.10.4 

import argparse
import os
import plistlib
import subprocess
import sys
import uuid

# Searches user's library for specified plist.
# Returns path to plist if it exists, None otherwise.
def getPlist(plist):
	user_home = os.path.join(os.path.expanduser('~'), 'Library')
	print "searching %s for %s." % (user_home, plist)
	paths = []
	for root, dirs, files in os.walk(user_home):
		# Ignore hidden directories and paths
		dirs[:] = [d for d in dirs if not d[0] == '.']
		files = [f for f in files if not f[0] == '.']
		if plist in files:
			path = os.path.join(root, plist)
			print "found: %s." % path
			paths.append(path)
	if len(paths) == 1:
		return paths[0]
	elif len(paths) > 1:
		print "More than one %s found, unsafe to continue." % (plist)
	else:
		print "%s not found in user Library." % (plist)
	return None

# Returns dict containing information read from plist file and
# a boolean value stating whether the plist had to be converted.
# Converts plist to xml1 form before reading if it is a binary plist.
def readPlist(plist_path):
	converted = False
	print "Reading %s into dict." % (plist_path)
	try:
		pl = plistlib.readPlist(plist_path)
	except:
		print "Plist appears to be in binary form, converting to xml."
		converted = True
		subprocess.call(['plutil', '-convert', 'xml1', plist_path])
		pl = plistlib.readPlist(plist_path)
	return pl, converted

# Adds a bookmark to the plist dictionary.
# If title of bookmark to be added is the same as a 
# preexisting bookmark the bookmark is skipped.
def addBookmark(plist, title, url):
	print "Checking for preexisting bookmarks title %s." % (title)
	if findTitle(plist, title):
		print "Found preexisting bookmark with title %s, skipping." % (title)
		return
	print "No preexisting bookmarks with title %s." % (title)
	print "Adding bookmark to %s with title %s." % (url, title)
	uri_dict = dict(
		title=title
	)
	bookmark = dict(
		WebBookmarkType='WebBookmarkTypeLeaf',
		WebBookmarkUUID=str(uuid.uuid5(uuid.NAMESPACE_DNS, title)),
		URLString=url,
		URIDictionary=uri_dict,
	)
	plist['Children'][1]['Children'].append(bookmark)

# Removes a bookmark from the plist dictionary.
# If the bookmark doesn't exist then skips
def removeBookmark(plist, title):
	print "Removing bookmark with title %s." % (title)
	if findTitle(plist, title, remove=True):
		print "Bookmark found and removed."
		return
	print "Could not find bookmark with title %s, skipping." % (title)

# Searches plist for bookmark with provided title
# Returns True if found, False otherwise
# If remove is True removes the bookmark if found
def findTitle(plist, title, remove=False):
	for bookmark in plist['Children'][1]['Children']:
		found_title = bookmark['URIDictionary']['title']
		if title == found_title:
			if remove:
				plist['Children'][1]['Children'].remove(bookmark)
			return True
	return False

# Removes all bookmarks from the plist dictionary
def removeAll(plist):
	print "Removing all bookmarks"
	# Remove bookmarks in reveresed order to avoid shifting issues
	for bookmark in reversed(plist['Children'][1]['Children']):
		title = bookmark['URIDictionary']['title']
		print "Removing bookmark w/ title %s." % (title)
		plist['Children'][1]['Children'].remove(bookmark)


# Writes plist to specified path.
# Converts to binary form after writing if binary=True.
def writePlist(plist, plist_path, binary=False):
	print "Writing modified plist to %s." % (plist_path)
	plistlib.writePlist(plist, plist_path)
	if binary:
		print "Converting %s to binary." % (plist_path)
		subprocess.call(['plutil', '-convert', 'binary1', plist_path])
	print "Done"

def main():
	parser = argparse.ArgumentParser(
		description='Command line tool for adding and removing Safari bookmarks in the context of the currently logged in user.',
	)
	parser.add_argument('--add', metavar='title|url', type=str, nargs='+', 
		help='double-colon seperated title and url of bookmark(s) to add in IE: --add MyWebsite::http://www.mywebsite.com MyOtherWebsite::http://www.myotherwebsite.com',
	)
	parser.add_argument('--remove', metavar='title', type=str, nargs='+', 
		help='title(s) of bookmark(s) to remove IE: --remove MyWebsite MyOtherWebsite',
	)
	parser.add_argument('--removeall', action='store_true', help='remove all current bookmarks')
	args = parser.parse_args()
	plist_path = getPlist('Bookmarks.plist')
	if plist_path is None:
		sys.exit(1)
	plist, converted = readPlist(plist_path)
	if args.removeall:
		removeAll(plist)
	if args.remove:
		for title in args.remove:
			removeBookmark(plist, title)
	if args.add:
		for bookmark in args.add:
			title, url = bookmark.split('::')
			addBookmark(plist, title, url)
	writePlist(plist, plist_path, binary=converted)


if __name__ == "__main__":
    main()
