#!/usr/bin/python

import argparse
import os
import plistlib
import subprocess
import sys
import uuid

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

def getPlist(plist):
    """
    Searches user's library for specified plist.

    Args:
        plist (str): Name of plist to search user's home directory for.

    Returns:
        Path to plist if a match is found.
        None otherwise.

    Raises:
        CalledProcessError if creation of plist fails.

    """
    user_home = os.path.expanduser('~/Library')
    print "searching %s for %s." % (user_home, plist)
    paths = []
    for root, dirs, files in os.walk(user_home):
        for file in files:
            # Skip hidden files
            if file[0] == '.':
                continue
            path = os.path.join(root, file)
            print "found: %s." % path
            paths.append(path)
    if len(paths) == 1:
        return paths[0]
    elif len(paths) > 1:
        print "More than one %s found, unsafe to continue." % (plist)
    else:
        print "%s not found in user Library." % (plist)
    return None

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
        plist (str): Plist dictionary to add bookmark to.
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
        plist (str): Plist dictionary to remove bookmark from.
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
        plist (str): Plist dictionary to search (and optionally remove bookmark from).
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

# Removes all bookmarks from the plist dictionary
def removeAll(plist):
    print "Removing all bookmarks."
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
