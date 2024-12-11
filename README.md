# Tinboard

![Tinboard](https://raw.githubusercontent.com/davep/tinboard/main/images/tinboard.png)

## Introduction

Tinboard is a terminal-based client application for the [Pinboard
bookmarking service](https://pinboard.in/about/). It provides the ability to
manage and search your bookmarks in the terminal.

**NOTE:** I've [moved away from using
Pinboard](https://blog.davep.org/2024/08/18/paindrop.html) and so won't be
adding more features to this application. I will attempt to support it where
possible, but please don't expect any changes that are anything other than a
simple bugfix.

## Installing

### pipx

The package can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install tinboard
```

Once installed run the `tinboard` command.

### Homebrew

The package is available via Homebrew. Use the following commands to install:

```sh
$ brew tap davep/homebrew
$ brew install tinboard
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

*NOTE: if it's your preference, you can set the token in an environment
variable called `TINBOARD_API_TOKEN`.*

## Using Tinboard

The best way to get to know Tinboard is to read the help screen, once in the
main application you can see this by pressing <kbd>F1</kbd>.

![Tinboard Help](https://raw.githubusercontent.com/davep/tinboard/main/images/help.png)

### Quick add on the command line

Tinboard has a (currently experimental) quick inline add feature. If you
run:

```sh
$ tinboard add
```

an inline version of the bookmark editor will be shown in your terminal,
allowing you to quickly add a bookmark and then carry on without running up
the full application.

## Getting help

If you need help, or have any ideas, please feel free to [raise an
issue](https://github.com/davep/tinboard/issues) or [start a
discussion](https://github.com/davep/tinboard/discussions).

[//]: # (README.md ends here)
