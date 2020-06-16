import re
from datetime import datetime
from typing import List, Optional
from .config import RELEASE_DATES

def tag_key(tagname: str) -> int:
    """
    Convert a tagname ("w.YYYY.NN" or "w.YYYY.N") into a key for sorting.

    "w_2017_1"  -> 201701
    "w_2017_01" -> 201701
    "w_2017_10" -> 201710
    etc.
    """
    return int(tagname.split("_")[1]) * 100 + int(tagname.split("_")[2])

def infer_release_date(tagname: str) -> Optional[datetime]:
    """Infer a release date from a version number.
    """
    if tagname in RELEASE_DATES:
        return RELEASE_DATES[tagname]
    elif tagname[0] == "w":
        # Must be a weekly!
        # Assume weeklies are released on Saturday (day number 6).
        return datetime.strptime(tagname + "_6", "w_%G_%V_%u")
    else:
        return None

def git_ref_from_eups_version(version: str) -> str:
    """Given a version string from the EUPS tag file, find something that
    looks like a Git ref.
    """
    match = re.match(r"(?P<tag>[a-z0-9._]+)(-\d+)?(-g(?P<sha>[a-z0-9]+))?(\+\d+)?", version)
    if match:
        if match.group('sha'):
            return match.group('sha')
        else:
            return match.group('tag')
    else:
        raise RuntimeError(f"Couldn't derive Git ref for {version}")
