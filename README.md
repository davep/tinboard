# Tinboard

![Tinboard](https://raw.githubusercontent.com/davep/tinboard/main/tinboard.png)

A very early work in progress. See below for the list of things still to do.

All application data lives in `~/.local/share/tinboard`; if you want to wipe
it out just nuke that directory. Likewise, application configuration data
lives in `~/.config/tinboard`.

As for bugs and feature requests and stuff... not yet thanks; that time will
come. :-)

Things to do:

- [X] Full text search.
- [X] Allow tags to be combined with core filters.
- [X] Allow both the above to be combined.
- [X] Add the ability to add a bookmark.
  - [X] Validation of data sent to the server
  - [X] Make available suggested tags once the bookmark is known.
- [X] Add the ability to edit a bookmark.
  - [X] Validation of data sent to the server
- [X] Add the ability to delete a bookmark.
- [X] Add the ability to quickly toggle the unread/read status of a
      bookmark.
- [X] Add the ability to quickly toggle the public/private status of a
      bookmark.
- [X] Add the ability to "logout" (IOW forget the API token).
- [ ] Add a bookmark export facility.
- [X] Add tag counts to the tag list.
- [X] Add tag searching to the command palette.
- [X] Add a show/hide toggle for the details pane.
- [ ] Add support for notes.
- [ ] Add saving of various states to resume when next ran.
  - [X] Dark/light mode.
  - [X] The show/hide state of the details pane.
  - [ ] The main filter?
  - [ ] The selected tag(s)?
- [X] All sorts of error handling
  - [X] Bad token given to Pinboard.
  - [X] IO errors around the local cache of bookmarks.

Known issues:

- Only the final tag in the tags for a bookmark is saving on the server.
  This is [a bug in
  `aiobinboard`](https://github.com/bachya/aiopinboard/issues/298).
- Newlines in the descriptions don't survive being pulled down from
  Pinboard. This is due to [`aiopinboard` using the XML API and that API
  endpoint not ensuring that line breaks can be
  handled](https://github.com/bachya/aiopinboard/issues/300). Solution here
  will be to either have `aiopinboard` switch to the JSON API endpoint, or
  to roll my own API client for this application.
- The description editor doesn't word-wrap. (currently waiting on Textual
  [to add wrapping support for
  `TextArea`](https://github.com/Textualize/textual/pull/3711)).

[//]: # (README.md ends here)
