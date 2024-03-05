# Tinboard ChangeLog

## WiP

**Released: WiP**

- Added tag command discovery hits to the command palette (that is, the
  command palette now pre-populates with all tag-based commands when first
  opened).
- Added filter command discovery hits to the command palette (that is, the
  command palette now pre-populates with all filter-based commands when
  first opened).
- Added bookmark command discovery hits to the command palette (that is, the
  command palette now pre-populates with all bookmark-based commands when
  first opened).

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
