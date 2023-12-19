# Tinboard

![Tinboard](https://raw.githubusercontent.com/davep/tinboard/main/tinboard.png)

## Introduction

Tinboard is a terminal-based client application for the [Pinboard
bookmarking service](https://pinboard.in/about/). It provides the ability to
manage and search your bookmarks in the terminal.

## Installing

The package can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install tinboard
```

Once installed run the `tinboard` command.

## Getting started

To use Tinboard you will need a Pinboard account (this application isn't
going to be useful to anyone who isn't a Pinboard user). Assuming you *do*
have a Pinboard account, you can get going by running up `tinboard` and
providing your API token when asked:

![The Tinboard token input dialog](https://raw.githubusercontent.com/davep/tinboard/main/images/token-request.png)

If you're not sure where to find your API token, just press <kbd>F1</kbd>,
or the `Go to token` button, and you'll be taken to the relevant Pinboard
page in your browser; copy the token, come back to this dialog and paste it
in.

Once done Tinboard will download your bookmarks and you're good to go!

## Using Tinboard

The best way to get to know Tinboard is to read the help screen, once in the
main application you can see this by pressing <kbd>F1</kbd>.

![Tinboard Help](https://raw.githubusercontent.com/davep/tinboard/main/images/help.png)

## Getting help

If you need help, or have any ideas, please feel free to [raise an
issue](https://github.com/davep/tinboard/issues) or [start a
discussion](https://github.com/davep/tinboard/discussions).

## Known issues

- The description editor doesn't word-wrap. (currently waiting on Textual
  [to add wrapping support for
  `TextArea`](https://github.com/Textualize/textual/pull/3711)).

## TODO

Things I'm considering adding or addressing:

- [ ] Double-check the rate limits on the API calls to be sure they're correct.
- [ ] A bookmark export facility.
- [ ] A bookmark availability checker.
  - [ ] Check the current bookmark.
  - [ ] A mode that slowly checks all bookmarks.
- [ ] Support for Pinboard Notes.
- [ ] Optionally sort the tags by count.

[//]: # (README.md ends here)
