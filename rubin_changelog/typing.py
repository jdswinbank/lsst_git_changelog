from typing import MutableMapping, Mapping, Union, Set

from .eups import EupsTag

# Should be a dataclass or something...
Changelog = MutableMapping[
    EupsTag, Mapping[str, Union[Set[str], Mapping[str, Set[str]]]]
]

