#!/usr/bin/python

import argparse
import os
import plistlib
import subprocess
import uuid

class SafariBookmarks(object):

	def __init__(self):
		self.plist_path = self.get()
		self.plist      = None
		self.titles     = None
		self.bookmarks  = None
		self.read()

	def get(self):
		"""
		Checks to see Bookmarks plist exists and has correct form. 
		If either of these conditions aren't met replaces existing plist with new empty one.

		Returns:
			Expanded path to ~/Library/Safari/Bookmarks.plist

		"""
		plist_path = os.path.expanduser('~/Library/Safari/Bookmarks.plist')
		if not os.path.isfile(plist_path):
			print "Bookmarks.plist doesn't appear to exist."
			print "Generating new Bookmarks.plist."
			self.generate(path)
		return plist_path

	def generate(self, plist_path):
		"""
		Generates a boilerplate Safari Bookmarks plist at plist path.

		Raises:
			CalledProcessError if creation of plist fails.

		"""
		subprocess.check_call(["touch", self.plist_path])
		contents = dict(
			Children=list((
				dict(
					Title="History",
					WebBookmarkIdentifier="History",
					WebBookmarkType="WebBookmarkTypeProxy",
					WebBookmarkUUID=str(uuid.uuid5(uuid.NAMESPACE_DNS, "History")),
				),
				dict(
					Children=list(),
					Title="BookmarksBar",
					WebBookmarkType="WebBookmarkTypeList",
					WebBookmarkUUID=str(uuid.uuid5(uuid.NAMESPACE_DNS, "BookmarksBar")),
				),
				dict(
					Title="BookmarksMenu",
					WebBookmarkType="WebBookmarkTypeList",
					WebBookmarkUUID=str(uuid.uuid5(uuid.NAMESPACE_DNS, "BookmarksMenu")),
				),
			)),
			Title="",
			WebBookmarkFileVersion=1,
			WebBookmarkType="WebBookmarkTypeList",
			WebBookmarkUUID=str(uuid.uuid5(uuid.NAMESPACE_DNS, "")),
		)
		plistlib.writePlist(contents, plist_path)

	def read(self):
		"""
		Parses plist into dictionary. Creates a new empty bookmarks plist if plist can't be read.

		Returns:
			Dictionary containing info parsed from bookmarks plist.

		"""
		subprocess.call(['plutil', '-convert', 'xml1', self.plist_path])
		try:
			pl = plistlib.readPlist(self.plist_path)
		except:
			print "Bookmarks.plist appears to be corrupted."
			print "Generating new Bookmarks.plist."
			self.generate() # if plist can't be read generate new empty one.
			pl = plistlib.readPlist(self.plist_path)
		self.plist     = pl
		self.bookmarks = self.plist['Children'][1]['Children']
		self.titles    = [bm["URIDictionary"]["title"] for bm in self.bookmarks if bm.get("URIDictionary") is not None]

	def add(self, title, url):
		"""
		Adds a bookmark to plist dictionary.

		Args:
			title (str): Title to label bookmark with.
			url   (str): Url to bookmark.

		"""
		if title in self.titles:
			print "Warning: Found preexisting bookmark with title %s, skipping." % (title)
			return

		bookmark = dict(
			WebBookmarkType='WebBookmarkTypeLeaf',
			WebBookmarkUUID=str(uuid.uuid5(uuid.NAMESPACE_DNS, title)),
			URLString=url,
			URIDictionary=dict(
				title=title
			),
		)
		self.bookmarks.append(bookmark)
		self.titles.append(title)

	def remove(self, title):
		"""
		Removes bookmark identified by title from plist dictionary if found.

		Args:
			title (str): Title bookmark is identified by.

		"""
		if title not in self.titles:
			return
		for bookmark in self.bookmarks:
			if bookmark.get("URIDictionary") and bookmark["URIDictionary"]["title"] == title:
				self.titles.remove(title)
				self.bookmarks.remove(bookmark)
				return

	def removeAll(self):
		"""
		Removes all bookmarks from the plist dictionary.

		"""
		# Remove bookmarks in reveresed order to avoid shifting issues
		for bookmark in reversed(self.bookmarks):
			self.bookmarks.remove(bookmark)

	def write(self):
		"""
		Writes modified plist dictionary to bookmarks plist and converts to binary format.

		"""
		plistlib.writePlist(self.plist, self.plist_path)
		subprocess.call(['plutil', '-convert', 'binary1', self.plist_path])

def main():
	parser = argparse.ArgumentParser(
		description='Command line tool for adding and removing Safari bookmarks in the context of the currently logged in user.',
	)
	parser.add_argument('--add', metavar='title::url', type=str, nargs='+', 
		help='double-colon seperated title and url of bookmark(s) to add in IE: --add MyWebsite::http://www.mywebsite.com MyOtherWebsite::http://www.myotherwebsite.com',
	)
	parser.add_argument('--remove', metavar='title', type=str, nargs='+', 
		help='title(s) of bookmark(s) to remove IE: --remove MyWebsite MyOtherWebsite',
	)
	parser.add_argument('--removeall', action='store_true', help='remove all current bookmarks')
	args = parser.parse_args()
	bookmarks = SafariBookmarks()
	if args.removeall:
		bookmarks.removeAll()
	if args.remove:
		for title in args.remove:
			bookmarks.remove(title)
	if args.add:
		for bookmark in args.add:
			title, url = bookmark.split('::')
			bookmarks.add(title, url)
	bookmarks.write()


if __name__ == "__main__":
	main()
