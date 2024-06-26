# Tinboard ChangeLog

## v0.15.1

**Released: 2024-06-23**

- Pinned Textual.

## v0.15.0

**Released: 2024-06-16**

- Unpinned Textual, fixed a couple of issues the recent versions have
  introduced, and attempted to undo questionable upstream cosmetic choices.

## v0.14.1

**Released: 2024-05-23**

- Pinned Textual to <=0.60.1 due to ongoing problems with later versions.

## v0.14.0

**Released: 2024-05-14**

- Added the ability to set the default value for new bookmark privacy.
  ([#50](https://github.com/davep/tinboard/pull/50))
- Added the ability to set the default value for new bookmark read-later
  status. ([#50](https://github.com/davep/tinboard/pull/50))
- Added an applications settings dialog.
  ([#50](https://github.com/davep/tinboard/pull/50))
- Added a command palette command for the applications settings dialog.
  ([#50](https://github.com/davep/tinboard/pull/50))

## v0.13.0

**Released: 2024-05-02**

- When copying a bookmark to the clipboard, a best effort is now made to
  ensure it'll also make it over a remote connection.
- Small cosmetic change to the bookmark input dialog to properly line up the
  description content with the rest of the inputs.

## v0.12.0

**Released: 2024-04-18**

- Added a dialog for checking if a bookmark is in the Wayback Machine.
  ([#44](https://github.com/davep/tinboard/pull/44))

## v0.11.1

**Released: 2024-04-09**

- Fixed an issue introduced in v0.11.0 where the "to read" flag wasn't being
  correctly read back in from the local copy of the bookmarks.

## v0.11.0

**Released: 2024-04-09**

- Updated to Textual v0.56.3
- Added a `--help` command line argument.
- Added a `--version` command line argument.
- Added a `--filter` command line argument.
- Added a `add` command line command, which shows the bookmark addition
  screen "inline" in the terminal, allows adding a new bookmark, then exits.
- Internal: changed the way that bookmarks are held and managed.

## v0.10.0

**Released: 2024-03-07**

- Added tag command discovery hits to the command palette (that is, the
  command palette now pre-populates with all tag-based commands when first
  opened).
- Added filter command discovery hits to the command palette (that is, the
  command palette now pre-populates with all filter-based commands when
  first opened).
- Added bookmark command discovery hits to the command palette (that is, the
  command palette now pre-populates with all bookmark-based commands when
  first opened).
- Added core command discovery hits to the command palette (that is, the
  command palette now pre-populates with all core commands when first
  opened).

## v0.9.0

**Released: 2024-02-29**

- Pressing <kbd>Escape</kbd> when in the "top-level" widget (so in the
  filters) now exits the application.

## v0.8.0

**Released: 2024-02-18**

- Updated to textual v0.51.0.
- Fixed filter-widget building crash on startup
  ([#26](https://github.com/davep/tinboard/issues/26)).

## v0.7.0

**Released: 2024-02-02**

- Updated to textual v0.48.2.
- Removed the custom `TextArea` in favour of the revamped native Textual
  one.
- Made some small cosmetic tweaks.

## v0.6.0

**Released: 2024-01-10**

- Fix tag suggestions being confused by a trailing space
  ([#21](https://github.com/davep/tinboard/issues/21)).

## v0.5.0

**Released: 2024-01-04**

- Full text search now searches within tags too.

## v0.4.0

**Released: 2023-12-25**

- Added the ability to copy a bookmark's URL to the clipboard.
- URL field will populate with any URL in the clipboard when adding a new
  bookmark.

## v0.3.0

**Released: 2023-12-23**

- Decluttered the footer in most cases; use of <kbd>F1</kbd> emphasised.
- Added the ability to sort the tags menu by bookmark count.

## v0.2.0

**Released: 2023-12-21**

- Added bookmark counts to the main filter menu.

## v0.1.0

**Released: 2023-12-19**

- Initial release.

[//]: # (ChangeLog.md ends here)
