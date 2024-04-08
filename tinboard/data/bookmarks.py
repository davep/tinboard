"""Code relating to the bookmarks file."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime
from json import JSONEncoder, dumps, loads
from pathlib import Path
from typing import Any, Iterator

##############################################################################
# pytz imports.
from pytz import UTC

##############################################################################
# Backward-compatible typing.
from typing_extensions import Self

##############################################################################
# Local imports.
from ..pinboard import API, BookmarkData
from .locations import data_dir


##############################################################################
def bookmarks_file() -> Path:
    """The path to the file that the local bookmarks are held in.

    Returns:
        The path to the bookmarks file.
    """
    return data_dir() / "bookmarks.json"


##############################################################################
class Bookmarks:
    """Class that holds the local copy of all the bookmarks."""

    def __init__(self) -> None:
        """Initialise the bookmarks."""
        super().__init__()
        self._bookmarks: list[BookmarkData] = []
        """The internal list of bookmarks."""
        self._index: dict[str, int] = {}
        """The index into the bookmarks."""
        self._last_downloaded: datetime | None = None
        """When the bookmarks were last downloaded."""

    @property
    def last_downloaded(self) -> datetime | None:
        """The time the bookmarks were last downloaded, or `None` if not yet."""
        return self._last_downloaded

    def _reindex(self) -> Self:
        """Reindex the bookmarks."""
        self._index = {
            bookmark.hash: index for index, bookmark in enumerate(self._bookmarks)
        }
        return self

    def mark_downloaded(self) -> Self:
        """Mark the bookmarks as having being downloaded at the time of calling."""
        self._last_downloaded = datetime.now(UTC)
        return self

    async def download(self, api: API) -> Self:
        """Download all available bookmarks from the server.

        Args:
            api: The API to download via.

        Returns:
            Self.
        """
        self._bookmarks = await api.all_bookmarks()
        return self._reindex().mark_downloaded()

    def _load_local_json(self, data: dict[str, Any]) -> Self:
        """Load the bookmarks from the given JSON data.

        Args:
            data: The data to load.

        Returns:
            Self.
        """
        self._last_downloaded = datetime.fromisoformat(data["last_downloaded"])
        self._bookmarks = [
            BookmarkData.from_json(bookmark) for bookmark in data["bookmarks"]
        ]
        return self._reindex()

    def load(self) -> Self:
        """Load the bookmarks from the local file.

        Returns:
            Self.
        """
        if bookmarks_file().exists():
            self._load_local_json(loads(bookmarks_file().read_text(encoding="utf-8")))
        return self

    class _Encoder(JSONEncoder):
        """Encoder for turning the bookmarks into JSON data."""

        def default(self, o: object) -> Any:
            """Handle unknown values.

            Args:
                o: The object to handle.
            """
            return datetime.isoformat(o) if isinstance(o, datetime) else o

    @property
    def _as_local_json(self) -> dict[str, Any]:
        """All the bookmarks as a JSON-friendly list."""
        return {
            "last_downloaded": None
            if self._last_downloaded is None
            else self._last_downloaded.isoformat(),
            "bookmarks": [bookmark.as_json for bookmark in self._bookmarks],
        }

    def save(self) -> Self:
        """Save the bookmarks to the local file.

        Returns:
            Self.
        """
        bookmarks_file().write_text(
            dumps(self._as_local_json, indent=4, cls=self._Encoder), encoding="utf-8"
        )
        return self

    def update_bookmark(self, bookmark: BookmarkData) -> Self:
        """Update the bookmarks with the given bookmark data.

        Args:
            bookmark: The bookmark data to update with.

        Returns:
            Self.

        Note:
            If the `hash` of the bookmark is known, the existing bookmark
            will be replaced with the new data. If the hash is unknown a
            brand new bookmark will be added to the collection.
        """
        # If the bookmark is already known...
        if (bookmark_index := self._index.get(bookmark.hash)) is not None:
            # ...replace it.
            self._bookmarks[bookmark_index] = bookmark
        else:
            # ...otherwise add it at the top of the list.
            self._bookmarks.insert(0, bookmark)
            self._reindex()
        return self

    def remove_bookmark(self, bookmark: BookmarkData) -> Self:
        """Remove the given bookmark data.

        Args:
            bookmark: The bookmark to remove.

        Returns:
            Self.
        """
        del self._bookmarks[self._index[bookmark.hash]]
        return self._reindex()

    @dataclass
    class Counts:
        """The various bookmark counts."""

        all: int = 0
        """The count of all the bookmarks."""
        unread: int = 0
        """The count of unread bookmarks."""
        read: int = 0
        """The count of read bookmarks."""
        private: int = 0
        """The count of private bookmarks."""
        public: int = 0
        """The count of public bookmarks."""
        untagged: int = 0
        """The count of untagged bookmarks."""
        tagged: int = 0
        """The count of tagged bookmarks."""

    @property
    def counts(self) -> Counts:
        """The various counts for the bookmarks."""
        # TODO: cache this.
        counts = self.Counts(all=len(self._bookmarks))
        for bookmark in self._bookmarks:
            if bookmark.to_read:
                counts.unread += 1
            else:
                counts.read += 1
            if bookmark.shared:
                counts.public += 1
            else:
                counts.private += 1
            if bookmark.tags:
                counts.tagged += 1
            else:
                counts.untagged += 1
        return counts

    @property
    def tags(self) -> list[str]:
        """All known tags used in the bookmarks."""
        tags: set[str] = set()
        for bookmark in self._bookmarks:
            tags |= set(tag for tag in bookmark.tag_list)
        return sorted(list(tags), key=str.casefold)

    def __len__(self) -> int:
        """Returns the number of bookmarks."""
        return len(self._bookmarks)

    def __bool__(self) -> bool:
        """`True` if there are bookmarks, `False` if not."""
        return bool(len(self))

    def __getitem__(self, index: str | int) -> BookmarkData:
        """Get a bookmark.

        Args:
            index: Either the hash of the bookmark, or its integer index.

        Returns:
            The bookmark data.
        """
        if isinstance(index, str):
            return self[self._index[index]]
        return self._bookmarks[index]

    def __iter__(self) -> Iterator[BookmarkData]:
        """An iterator over the bookmarks."""
        return iter(self._bookmarks)


### bookmarks.py ends here
