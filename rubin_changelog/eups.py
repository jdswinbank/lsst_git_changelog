import yaml

from typing import Dict, Set
from urllib.request import urlopen

from rubin_changelog.config import EUPS_PKGROOT, REPOS_YAML

class Eups(object):
    def __init__(self, *, pkgroot: str = EUPS_PKGROOT):
        self.__pkgroot = pkgroot

    def products_for_tag(self, tagname: str) -> Set[str]:
        u = urlopen(f"{self.__pkgroot}/tags/{tagname}.list")
        products = set()
        for line in u.read().decode("utf-8").strip().split("\n"):
            if line.startswith("EUPS distribution "):
                continue
            if line.strip()[0] == "#":
                continue
            else:
                products.add(line.split()[0])
        return products

def get_urls_for_packages(packages: Set[str], repos_yaml: str = REPOS_YAML) -> Dict[str, Dict[str, str]]:
    pkgs = {}
    with urlopen(repos_yaml) as u:
        y = yaml.safe_load(u)
        for pkg in packages:
            if isinstance(y[pkg], str):  # Must be a URL
                pkgs[pkg] = {'url': y[pkg]}
            else:
                pkgs[pkg] = y[pkg]
    return pkgs
