"""Pinboard API code."""

##############################################################################
# Python imports.
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from functools import reduce
from hashlib import md5
from json import loads
from operator import or_
from typing_extensions import Final

##############################################################################
# pytz imports.
from pytz import UTC

##############################################################################
# HTTPX imports.
import httpx


##############################################################################
def parse_time(text: str) -> datetime:
    """Parse a time from the Pinboard API.

    Args:
        text: The text version of the time to parse.

    Returns:
        The parsed time.

    Pinboard returns times ending in a `Z`. Python doesn't seem capable of
    parsing that. So we swap that for a `+00:00` and then parse.
    """
    return datetime.fromisoformat(text.removesuffix("Z") + "+00:00")


##############################################################################
@dataclass
class BookmarkData:
    """Pinboard bookmark data."""

    href: str
    """The URL for the bookmark."""

    description: str
    """The description (AKA title) of the bookmark."""

    extended: str
    """The extended description of the bookmark."""

    hash: str
    """The hash for the bookmark."""

    time: datetime
    """The time of the bookmark's modification."""

    shared: bool
    """Is the bookmark shared with the public?"""

    to_read: bool
    """Is the bookmark unread?"""

    tags: str
    """The tags for the bookmark, space-separated."""

    def __post_init__(self) -> None:
        """Final initialisation of the bookmark data.

        If `hash` is empty, one will be generated.
        """
        if not self.hash:
            self.hash = md5(self.href.encode()).hexdigest()

    @classmethod
    def from_json(cls, data: dict[str, str]) -> "BookmarkData":
        """Create an instance of `BookmarkData` from JSON data.

        Args:
            data: The data to create the bookmark instance from.

        Returns:
            An instance of `BookmarkData`.
        """
        return cls(
            href=data.get("href", ""),
            description=data.get("description", ""),
            extended=data.get("extended", ""),
            hash=data.get("hash", ""),
            time=parse_time(data.get("time", "")),
            shared=data.get("shared", "") == "yes",
            to_read=data.get("toread", "") == "yes",
            tags=data.get("tags", ""),
        )

    @property
    def as_json(self) -> dict[str, str]:
        """The bookmark in JSON-friendly form."""
        return asdict(self)


##############################################################################
class API:
    """Pinboard API client class."""

    AGENT: Final[str] = "Tinboard (https://github.com/davep/tinboard)"
    """The agent string to use when talking to the API."""

    class Error(Exception):
        """Exception for any sort of error calling on the API."""

    class RequestError(Error):
        """An exception raised if there was a problem making the request."""

    class PinboardError(Error):
        """An exception raised if the Pinboard API raised an error."""

    def __init__(self, api_token: str) -> None:
        """Initialise the API object.

        Args:
            api_token: The API token to use.
        """
        self._api_token = api_token
        """The API token for the user."""
        self._all_cache: list[BookmarkData] = []
        """The cache of all bookmarks; used if we've grabbed them and we're calling for them again too soon."""
        self._last_all: datetime | None = None
        """The time when we last asked for all the bookmarks."""

    def _api_url(self, *path: str) -> str:
        """Construct a URL for calling on the API.

        Args:
            *path: The path to the endpoint.

        Returns:
            The URL to use.
        """
        return f"https://api.pinboard.in/v1/{'/'.join(path)}?auth_token={self._api_token}&format=json"

    async def _call(self, *path: str, **params: str) -> str:
        """Call on the Pinboard API.

        Args:
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            The text returned from the call.

        Raises:
            API.RequestError: If there was an error making the request.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self._api_url(*path),
                    params=params,
                    headers={"user-agent": self.AGENT},
                )
            except httpx.RequestError as error:
                raise self.RequestError(str(error))
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as error:
                raise self.RequestError(str(error))
            return response.text

    @classmethod
    def _check(cls, data: dict[str, str]) -> dict[str, str]:
        """Check if there's any sort of problem reported in the data.

        Args:
            data: The data to check.

        Returns:
            The data.

        Raises:
            API.PinboardError: If a problem was found.
        """
        if "code" in data and data["code"] != "done":
            raise cls.PinboardError(data["code"])
        return data

    async def last_update(self) -> datetime:
        """Get when the bookmarks were last updated on Pinboard.

        Returns:
            The time when the last update took place.
        """
        return parse_time(loads(await self._call("posts", "update"))["update_time"])

    _ALL_LIMIT: Final[timedelta] = timedelta(minutes=5)
    """The rate limit for getting all bookmarks."""

    async def _all_too_soon(self) -> bool:
        """Is it too soon to be getting all the bookmarks?"""
        # It's not too soon if we haven't grabbed everything yet.
        if self._last_all is None:
            return False
        # If we're within the rate limit, we also say that's too soon.
        if (datetime.now(UTC) - self._last_all) < self._ALL_LIMIT:
            return True
        # Finally, it is too soon if the server hasn't been updated.
        if (await self.last_update()) < self._last_all:
            return True
        return False

    async def all_bookmarks(self) -> list[BookmarkData]:
        """Get all the bookmarks available on the server.

        Returns:
            All the bookmarks.
        """
        # If we're hitting the API way too soon after a previous request...
        if await self._all_too_soon():
            # ...just go with the cached version.
            return self._all_cache
        self._all_cache = [
            BookmarkData.from_json(bookmark)
            for bookmark in loads(await self._call("posts", "all"))
        ]
        self._last_all = datetime.now(UTC)
        return self._all_cache

    @dataclass
    class TagSuggestions:
        """Type of data that holds tag suggestions for a URL."""

        url: str
        """The URL that the suggestions are for."""
        popular: list[str]
        """The popular tags."""
        recommended: list[str]
        """The recommended tags."""

    async def suggested_tags(self, url: str) -> TagSuggestions:
        """Get the suggested tags for the given URL.

        Args:
            url: The URL to get the suggestions for.

        Returns:
            The suggested tags for the URL.
        """
        suggestions = reduce(or_, loads(await self._call("posts", "suggest", url=url)))
        return self.TagSuggestions(
            url,
            popular=suggestions.get("popular", []),
            recommended=suggestions.get("recommended", []),
        )

    async def add_bookmark(self, data: BookmarkData) -> None:
        """Add the given bookmark to the server.

        Args:
            data: The bookmark to add.
        """
        self._check(
            loads(
                await self._call(
                    "posts",
                    "add",
                    url=data.href,
                    description=data.description,
                    extended=data.extended,
                    tags=data.tags,
                    dt=data.time.isoformat(),
                    replace="yes",
                    shared="yes" if data.shared else "no",
                    toread="yes" if data.to_read else "no",
                )
            )
        )

    async def delete_bookmark(self, url: str) -> None:
        """Delete the bookmark associated with a URL.

        Args:
            url: The URL to delete the bookmark for.
        """
        await self._call("posts", "delete", url=url)


### api.py ends here
