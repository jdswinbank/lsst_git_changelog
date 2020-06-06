import yaml

from typing import Dict
from urllib.request import urlopen

from rubin_changelog.config import REPOS_YAML

class Repos(object):
    def __init__(self, *, repos_yaml: str = REPOS_YAML):
        with urlopen(repos_yaml) as u:
            self.__yaml = yaml.safe_load(u)

    def __getitem__(self, product: str) -> Dict[str, str]:
        if isinstance(self.__yaml[product], str):  # Must be a URL
            return {'url': self.__yaml[product]}
        else:
            return self.__yaml[product]
