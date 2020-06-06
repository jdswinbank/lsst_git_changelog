def tag_key(tagname: str) -> int:
    """
    Convert a tagname ("w.YYYY.NN" or "w.YYYY.N") into a key for sorting.

    "w.2017.1"  -> 201701
    "w.2017.01" -> 201701
    "w.2017.10" -> 201710
    etc.
    """
    return int(tagname.split(".")[1]) * 100 + int(tagname.split(".")[2])
