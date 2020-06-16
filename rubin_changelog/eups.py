import logging
import re

from datetime import datetime
from urllib.request import urlopen
from collections import Mapping
from subprocess import CalledProcessError

from typing import Any, Iterable, Iterator, List, Tuple, Set, Optional

from lxml import html  # type: ignore

from .config import EUPS_PKGROOT, TAG_SKIPLIST, PRODUCT_SKIPLIST
from .utils import infer_release_date, git_ref_from_eups_version


class EupsTag(object):
    def __init__(
        self,
        name: str,
        candidate_date: datetime,
        product_list: Iterable[Tuple[str, str]],
    ):
        self.name = name
        self.products = [product[0] for product in product_list]

        # IF we can infer a release date based on the tag name, then use that.
        # Otherwise, use the candidate date supplied (e.g. from HTTP).
        self.date = infer_release_date(self.name) or candidate_date

        for (product_name, product_version) in product_list:
            if self.name == "master":
                continue
            from .products import products

            try:
                product = products[product_name]
            except KeyError as e:
                logging.warning(f"Repository for {product_name} not available: {e}")
            else:
                if self.name not in product.tags:
                    try:
                        # If we know the correct version, tag it directly...
                        product.add_tag(
                            self.name, git_ref_from_eups_version(product_version)
                        )
                    except CalledProcessError as e:
                        # ...otherwise, add a tag based on date.
                        logging.warning(
                            f"Failed to tag {product_name} with version "
                            f"{git_ref_from_eups_version(product_version)}: "
                            f"Git said: \"{e.output.decode('utf-8').strip()}\" "
                            f"Falling back to timestamp."
                        )
                        date_sha = products[product_name].sha_for_date(self.date)
                        product.add_tag(self.name, date_sha)

    def __lt__(self, other):
        logging.info(f"{self.name}, {self.date}")
        logging.info(f"{other.name}, {self.date}")
        return self.date < other.date


class Eups(Mapping):
    def __init__(self, *, pkgroot: str = EUPS_PKGROOT, pattern: str = "w_latest"):
        self._pkgroot = pkgroot
        self._pattern = pattern
        self._tags = {
            tag_name: self.__retrieve_tag(tag_name)
            for tag_name in self.__retrieve_tag_list()
        }

    def __retrieve_tag_list(self) -> List[str]:
        logging.debug(f"Fetching tag list")
        h = html.parse(urlopen(self._pkgroot + "/tags"))
        return [
            el.text[:-5]
            for el in h.findall("./body/table/tr/td/a")
            if el.text[-5:] == ".list"
            and re.match(self._pattern, el.text)
            and not el.text[:-5] in TAG_SKIPLIST
        ]

    def __retrieve_tag(self, tag_name: str) -> EupsTag:
        logging.debug(f"Fetching tag {tag_name}")
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
                product_name, _, product_version = line.split()
                if product_name not in PRODUCT_SKIPLIST:
                    products.append((product_name, product_version))
        return EupsTag(tag_name, tag_date, products)

    def __getitem__(self, tag_name: str) -> EupsTag:
        return self._tags[tag_name]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._tags)

    def __len__(self) -> int:
        return len(self._tags)

    @property
    def all_products(self) -> Set[str]:
        products = set()
        for tag in self.values():
            products.update(tag.products)
        return products
