# SafariBookmarkEditor
CLI tool for adding and removing Safari bookmarks in the context of the currently logged in user.
Used to add and remove bookmarks on a user basis. On fresh installs that lack a Bookmarks.plist 
in the ~/Library/Safari/ folder or in the case of a corrupt Bookmarks.plist the script will delete
the current Bookmarks.plist and generate a new one with the proper format. Bookmark titles are 
checked against those already in the Bookmarks.plist to ensure no collisions occur.


usage: SafariBookmarkEditor.py [-h] [--add title::url [title::url ...]]
                               [--remove title [title ...]] [--removeall]

Command line tool for adding and removing Safari bookmarks in the context of
the currently logged in user.

optional arguments:
  -h, --help            show this help message and exit
  --add title::url [title::url ...]
                        double-colon seperated title and url of bookmark(s) to
                        add in IE: --add MyWebsite::http://www.mywebsite.com
                        MyOtherWebsite::http://www.myotherwebsite.com
  --remove title [title ...]
                        title(s) of bookmark(s) to remove IE: --remove
                        MyWebsite MyOtherWebsite
  --removeall           remove all current bookmarks
