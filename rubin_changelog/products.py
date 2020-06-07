import logging

from .config import TARGET_DIR
from .repos_yaml import ReposYaml
from .repository import Repository

class Products(object):
    def __init__(self):
        self._repos_yaml = ReposYaml()
        self._products = {}

    def __getitem__(self, product_name: str) -> Repository:
        if product_name not in self._products:
            logging.debug(f"Materializing {product_name}")
            self._products[product_name] = Repository.materialize(
                self._repos_yaml[product_name]["url"],
                TARGET_DIR,
                branch_name=self._repos_yaml[product_name].get("ref", "master"),
            )
        return self._products[product_name]
