import dbm
import json
import logging

from urllib.request import urlopen
from urllib.error import URLError

from rubin_changelog.config import JIRA_API_URL, TICKET_CACHE


class JiraCache(object):
    def __init__(
        self, *, api_root: str = JIRA_API_URL, cache_location: str = TICKET_CACHE
    ):
        self.__api_root = api_root
        self.__cache_location = cache_location

    def __url_for_ticket(self, ticket: str) -> str:
        return f"{self.__api_root}/issue/{ticket}?fields=summary"

    def __getitem__(self, ticket: str) -> str:
        with dbm.open(self.__cache_location, "c") as db:  # type: ignore[attr-defined]
            if ticket not in db:
                url = self.__url_for_ticket(ticket)
                logging.debug(url)
                try:
                    db[ticket] = json.load(urlopen(url))["fields"]["summary"].encode(
                        "utf-8"
                    )
                except URLError:
                    return "Ticket description not available"
            return db[ticket].decode("utf-8")
