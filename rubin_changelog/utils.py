def tag_key(tagname: str) -> int:
    """
    Convert a tagname ("w.YYYY.NN" or "w.YYYY.N") into a key for sorting.

    "w_2017_1"  -> 201701
    "w_2017_01" -> 201701
    "w_2017_10" -> 201710
    etc.
    """
    return int(tagname.split("_")[1]) * 100 + int(tagname.split("_")[2])
