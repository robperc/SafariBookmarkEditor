# SafariBookmarkEditor
CLI tool for adding and removing Safari bookmarks in the context of the currently logged in user.
Used to add and remove bookmarks on a user basis. On fresh installs that lack a Bookmarks.plist 
in the ~/Library/Safari/ folder or in the case of a corrupt Bookmarks.plist the script will delete
the current Bookmarks.plist and generate a new one with the proper format. Bookmark titles are 
checked against those already in the Bookmarks.plist to ensure no collisions occur.
