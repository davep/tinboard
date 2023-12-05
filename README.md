# Tinboard

![Tinboard](https://raw.githubusercontent.com/davep/tinboard/main/tinboard.png)

A very early work in progress. This will be turning into a full
terminal-based Pinboard client. At the moment this is a read-only client;
something to let me riff on the interface and decide what I like. Once that
has settled down I'll be adding full write capability too.

All application data lives in `~/.local/share/tinboard`; if you want to wipe
it out just nuke that directory. Likewise, application configuration data
lives in `~/.config/tinboard`.

As for bugs and feature requests and stuff... not yet thanks; that time will
come. :-)

Things to do:

- [ ] Full text search.
- [ ] Allow tags to be combined with core filters.
- [ ] Allow both the above to be combined.
- [X] Add the ability to add a bookmark.
  - [X] Validation of data sent to the server
  - [ ] Make available suggested tags once the bookmark is known.
- [X] Add the ability to edit a bookmark.
  - [X] Validation of data sent to the server
- [X] Add the ability to delete a bookmark.
- [X] Add the ability to quickly toggle the unread/read status of a
      bookmark.
- [X] Add the ability to quickly toggle the public/private status of a
      bookmark.
- [ ] Add the ability to "logout" (IOW forget the API token).
- [ ] Add a bookmark export facility.
- [ ] Add tag counts to the tag list.
- [X] Add tag searching to the command palette.
- [ ] Add a show/hide toggle for the details pane.
- [ ] Add support for notes.
- [ ] Add saving of various states to resume when next ran.
  - [X] Dark/light mode.
  - [ ] The show/hide state of the details pane.
  - [ ] The main filter?
  - [ ] The selected tag(s)?
- [ ] All sorts of error handling
  - [ ] Bad token given to Pinboard.
  - [ ] IO errors around the local cache of bookmarks.

[//]: # (README.md ends here)
