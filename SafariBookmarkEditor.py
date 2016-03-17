#!/usr/bin/python

import argparse
import os
import plistlib
import subprocess
import sys
import uuid

class SafariBookmarks(object):

    def __init__(self):
        self.plist_path = getBookmarksPlist()
        self.plist      = None
        self.bookmarks  = None
        self.update

    def generate(self):
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
        plistlib.writePlist(contents, self.plist_path)

    def read(self):
        """
        Parses plist into dictionary. Creates a new empty bookmarks plist if plist can't be read.

        Returns:
            Dictionary containing info parsed from bookmarks plist.

        """
        try:
            pl = plistlib.readPlist(self.plist_path)
        except:
            print "Bookmarks.plist appears to be corrupted."
            print "Generating new Bookmarks.plist."
            self.generate() # if plist can't be read generate new empty one.
            pl = plistlib.readPlist(self.plist_path)
        return pl

    def add(self, title, url):
        """
        Adds a bookmark to plist dictionary.

        Args:
            title (str): Title to label bookmark with.
            url   (str): Url to bookmark.

        """
        if self.findTitle(title):
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
        self.children.append(bookmark)

    def remove(self, title):
        """
        Removes bookmark identified by title from plist dictionary if found.

        Args:
            title (str): Title bookmark is identified by.

        """
        if self.findTitle(title, remove=True):
            print "Bookmark with title '%s' found and removed." % (title)
            return
        print "Could not find bookmark with title %s, skipping." % (title)

    def removeAll(self):
        """
        Removes all bookmarks from the plist dictionary.

        """
        print "Removing all bookmarks."
        # Remove bookmarks in reveresed order to avoid shifting issues
        for bookmark in reversed(self.children):
            title = bookmark['URIDictionary']['title']
            print "Removing bookmark w/ title %s." % (title)
            self.children.remove(bookmark)

    def findTitle(self, title, remove=False):
        """
        Boolean test to check if bookmark identified by title exists in plist dictionary.
        Bookmark identified by title can optionally be removed if specified.

        Args:
            title (str): Title bookmark is identified by.
            remove (Optional(bool)): Remove bookmark identified by title (if found) if set to True.
        
        Returns:
            True if bookmark identified by title is found.
            False otherwise.

        """
        for bookmark in self.children:
            found_title = bookmark['URIDictionary']['title']
            if title == found_title:
                if remove:
                    plist['Children'][1]['Children'].remove(bookmark)
                return True
        return False

def genBookmarksPlist(plist_path):
    """
    Generates a boilerplate Safari Bookmarks plist at plist path.

    Args:
        plist_path (str): Path to generate boilerplate Safari bookmarks plist at.

    Raises:
        CalledProcessError if creation of plist fails.

    """
    subprocess.check_call(["touch", plist_path])
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
    subprocess.call(['plutil', '-convert', 'binary1', plist_path])

def getBookmarksPlist():
    """
    Checks to see Bookmarks plist exists and has correct form. 
    If either of these conditions aren't met replaces existing plist with new empty one.

    Returns:
        Expanded path to ~/Library/Safari/Bookmarks.plist

    """
    print "Checking to ensure Bookmarks.plist exists."
    plist_path = os.path.expanduser('~/Library/Safari/Bookmarks.plist')
    if not os.path.isfile(plist_path):
        print "Bookmarks.plist doesn't appear to exist."
        print "Generating new Bookmarks.plist."
        genBookmarksPlist(plist_path)
    return plist_path

def readBookmarksPlist(plist_path):
    """
    Parses plist into dictionary. Converts plist to xml form before reading if it is a binary plist.

    Args:
        plist_path (str): Path of plist to parse.

    Returns:
        (Dictionary, True) if plist was converted to xml form before parsing.
        (Dictionary, False) otherwise.

    """
    converted = False
    try:
        pl = plistlib.readPlist(plist_path)
    except:
        print "Plist appears to be in binary form, converting to xml."
        converted = True
        subprocess.call(['plutil', '-convert', 'xml1', plist_path])
    try:
        pl = plistlib.readPlist(plist_path)
    except:
        print "Bookmarks.plist appears to be corrupted."
        print "Generating new Bookmarks.plist."
        converted = True
        genBookmarksPlist(plist_path)
        subprocess.call(['plutil', '-convert', 'xml1', plist_path])
        pl = plistlib.readPlist(plist_path)
    return pl, converted

def addBookmark(plist, title, url):
    """
    Adds a bookmark to plist dictionary.

    Args:
        plist (dict(str: str, ..., str: str)): Plist dictionary to add bookmark to.
        title (str): Title to label bookmark with.
        url   (str): Url to bookmark.

    """
    print "Attempting to add bookmark for %s with title %s." % (url, title)
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

def removeBookmark(plist, title):
    """
    Removes bookmark identified by title from plist dictionary if found.

    Args:
        plist (dict(str: str, ..., str: str)): Plist dictionary to remove bookmark from.
        title (str): Title bookmark is identified by.

    """
    print "Attempting to remove bookmark with title %s." % (title)
    if findTitle(plist, title, remove=True):
        print "Bookmark found and removed."
        return
    print "Could not find bookmark with title %s, skipping." % (title)

def findTitle(plist, title, remove=False):
    """
    Boolean test to check if bookmark identified by title exists in plist dictionary.
    Bookmark identified by title can optionally be removed if specified.

    Args:
        plist (dict(str: str, ..., str: str)): Plist dictionary to search (and optionally remove bookmark from).
        title (str): Title bookmark is identified by.
        remove (Optional(bool)): Remove bookmark identified by title (if found) if set to True.
    
    Returns:
        True if bookmark identified by title is found.
        False otherwise.

    """
    for bookmark in plist['Children'][1]['Children']:
        found_title = bookmark['URIDictionary']['title']
        if title == found_title:
            if remove:
                plist['Children'][1]['Children'].remove(bookmark)
            return True
    return False

def removeAll(plist):
	"""
	Removes all bookmarks from the plist dictionary.

	Args:
		plist (dict(str: str, ..., str: str)): Plist dictionary to remove all bookmarks from.

	"""
    print "Removing all bookmarks."
    # Remove bookmarks in reveresed order to avoid shifting issues
    for bookmark in reversed(plist['Children'][1]['Children']):
        title = bookmark['URIDictionary']['title']
        print "Removing bookmark w/ title %s." % (title)
        plist['Children'][1]['Children'].remove(bookmark)

def writePlist(plist, plist_path, binary=False):
    """
    Writes plist dictionary to file at path.

    Args:
        plist (dict(str: str, ..., str: str)): Plist dictionary to remove all bookmarks from.
        plist_path (str): Path to write plist.

    Keyword Args:
        binary (bool): Whether the plist should be written in binary format.
                       Defaults to False.

    """
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
    parser.add_argument('--add', metavar='title::url', type=str, nargs='+', 
        help='double-colon seperated title and url of bookmark(s) to add in IE: --add MyWebsite::http://www.mywebsite.com MyOtherWebsite::http://www.myotherwebsite.com',
    )
    parser.add_argument('--remove', metavar='title', type=str, nargs='+', 
        help='title(s) of bookmark(s) to remove IE: --remove MyWebsite MyOtherWebsite',
    )
    parser.add_argument('--removeall', action='store_true', help='remove all current bookmarks')
    args = parser.parse_args()
    plist_path = getBookmarksPlist()
    if plist_path is None:
        sys.exit(1)
    plist, converted = readBookmarksPlist(plist_path)
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
