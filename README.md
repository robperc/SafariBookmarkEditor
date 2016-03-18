# SafariBookmarkEditor
Python module for easily adding, removing, and moving positions of Safari bookmarks in the context of the currently logged in user.
On fresh installs that lack a Bookmarks.plist in the ~/Library/Safari/ folder or in the case of a corrupt plist a boilerplate Bookmarks plist will be generated with the proper format. Bookmark titles are checked against existing bookmarks to ensure no collisions occur. Can also be run as a CLI tool.

Example Usage:
```
#!/usr/bin/python

from SafariBookmarkEditor import SafariBookmarks          # Import the module

bookmarks = SafariBookmarks()                             # Create a Safari Bookmarks instance to act on.

bookmarks.add("Reddit", "https://reddit.com")             # Add bookmark for Reddit
bookmarks.add("Apple", "https://www.apple.com", index=0)  # Add bookmark for Apple at 0th position
bookmarks.swap("Apple", "Reddit")                         # Swap positions of Apple and Reddit bookmarks
bookmarks.move("Apple", 0)                                # Move Apple bookmark back to 0th position
bookmarks.remove("Apple")                                 # Remove the Apple bookmark

bookmarks.write()                                         # Write changes to Bookmarks plist

```

CLI Usage:
```
./SafariBookmarkEditor.py -h
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
```
