import yaml

from datetime import datetime
from typing import Dict, Set
from urllib.request import urlopen

from typing import Iterable

from .config import EUPS_PKGROOT, TARGET_DIR, DEBUG
from .repository import Repository


class EupsTag(object):
    def __init__(self, name: str, date: datetime, products: Iterable[str]):
        self.name = name
        self.date = date
        self.products = products


class Eups(object):
    def __init__(self, *, pkgroot: str = EUPS_PKGROOT):
        self._pkgroot = pkgroot
        self._tags = {}

    def __retrieve_tag(self, tag_name: str) -> EupsTag:
        u = urlopen(f"{self._pkgroot}/tags/{tag_name}.list")
        tag_date = datetime.strptime(u.info()['last-modified'],
                                             "%a, %d %b %Y %H:%M:%S %Z")
        products = []
        for line in u.read().decode("utf-8").strip().split("\n"):
            if line.startswith("EUPS distribution "):
                continue
            if line.strip()[0] == "#":
                continue
            else:
                products.append(line.split()[0])
        return EupsTag(tag_name, tag_date, products)

    def __getitem__(self, tag_name: str) -> EupsTag:
        if tag_name not in self._tags:
            self._tags[tag_name] = self.__retrieve_tag(tag_name)
        return self._tags[tag_name]
