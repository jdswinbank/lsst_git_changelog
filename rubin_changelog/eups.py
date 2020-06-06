import re

from datetime import datetime
from urllib.request import urlopen
from collections import Mapping

from typing import Any, Iterable, Iterator, List

from lxml import html

from .config import EUPS_PKGROOT


class EupsTag(object):
    def __init__(self, name: str, date: datetime, products: Iterable[str]):
        self.name = name
        self.date = date
        self.products = products


class Eups(Mapping):
    def __init__(self, *, pkgroot: str = EUPS_PKGROOT, pattern: str = "w_20"):
        self._pkgroot = pkgroot
        self._pattern = pattern
        self._tags = {
            tag_name: self.__retrieve_tag(tag_name)
            for tag_name in self.__retrieve_tag_list()
        }

    def __retrieve_tag_list(self) -> List[str]:
        h = html.parse(urlopen(self._pkgroot + "/tags"))
        return [
            el.text[:-5]
            for el in h.findall("./body/table/tr/td/a")
            if el.text[-5:] == ".list" and re.match(self._pattern, el.text)
        ]

    def __retrieve_tag(self, tag_name: str) -> EupsTag:
        u = urlopen(f"{self._pkgroot}/tags/{tag_name}.list")
        tag_date = datetime.strptime(
            u.info()["last-modified"], "%a, %d %b %Y %H:%M:%S %Z"
        )
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
        return self._tags[tag_name]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._tags)

    def __len__(self) -> int:
        return len(self._tags)
