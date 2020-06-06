import dbm
import json
import os

from urllib.request import urlopen
from urllib.error import HTTPError

from rubin_changelog.config import DEBUG, JIRA_API_URL, TICKET_CACHE


def get_ticket_summary(
    ticket: str, *, api_root: str = JIRA_API_URL, cache: str = TICKET_CACHE
):
    with dbm.open(cache, "c") as db:  # type: ignore[attr-defined]
        if ticket not in db:
            url = f"{JIRA_API_URL}/issue/{ticket}?fields=summary"
            if DEBUG:
                print(url)
            try:
                db[ticket] = json.load(urlopen(url))["fields"]["summary"].encode(
                    "utf-8"
                )
            except HTTPError:
                return "Ticket description not available"
        return db[ticket].decode("utf-8")
