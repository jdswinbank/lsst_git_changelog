import os
import datetime

DEBUG = False
JIRA_API_URL = "https://jira.lsstcorp.org/rest/api/2"
EUPS_PKGROOT = "https://eups.lsst.codes/stack/src/"
REPOS_YAML = "https://raw.githubusercontent.com/lsst/repos/master/etc/repos.yaml"

# Location in which we'll store (bare) repositories.
# Should match the cached location in GitHub Actions.
TARGET_DIR = os.path.expanduser("~/repos")

# Should be within the above so tha it's also cached.
TICKET_CACHE = os.path.join(TARGET_DIR, "ticket.cache")

# These products are skipped because they are huge (and so blow our storage
# quota in GitHub Actions) but don't add much interesting information.
PRODUCT_SKIPLIST = [
    "boost",
    "galsim",
    "mariadb",
    "mariadbclient",
    "qserv_distrib",
    "qserv_testdata",
    "sims_skybrightness_data",
]
TAG_SKIPLIST = ["w_2019_30", "v12_1_1", "v12_1_2_rc1", "v12_1_2"]

RELEASE_DATES = {
    # Dates for these releases are all bad (uniformly set to 2017-04-11) on
    # the distribution server.
    # The dates here are inferred based on the tag date in afw, except as
    # otherwise noted.
    "v10_0": datetime.datetime(2014, 12, 9, 8, 23, 14, 0),
    "v10_1_rc1": datetime.datetime(2015, 5, 12, 21, 29, 43, 0),  # inferred from successor
    "v10_1_rc2": datetime.datetime(2015, 5, 12, 21, 29, 44, 0),  # inferred from successor
    "v10_1_rc3": datetime.datetime(2015, 5, 12, 21, 29, 45, 0),  # inferred from successor
    "v10_1": datetime.datetime(2015, 5, 12, 21, 29, 45, 0),
    "v11_0_rc1": datetime.datetime(2015, 9, 10, 3, 30, 31, 0),  # inferred from successor
    "v11_0_rc2": datetime.datetime(2015, 9, 10, 3, 30, 31, 0),
    "v11_0_rc3": datetime.datetime(2015, 9, 10, 3, 30, 48, 0),  # inferred from successor
    "v11_0": datetime.datetime(2015, 9, 24, 4, 42, 49, 0),
    "v11_1_rc1": datetime.datetime(2015, 11, 24, 17, 4, 52, 0),  # inferred from date of last commit on afw
    "v12_0_rc1": datetime.datetime(2016, 5, 24, 9, 26, 27, 0),
    "v12_0": datetime.datetime(2016, 6, 15, 19, 2, 59, 0),
    "v12_1_rc1": datetime.datetime(2016, 9, 7, 13, 27, 11, 0),
    "v12_1": datetime.datetime(2016, 9, 21, 4, 54, 20, 0),
    "v13_0_rc1": datetime.datetime(2017, 2, 16, 16, 3, 5, 0),
    "v13_0": datetime.datetime(2017, 2, 28, 4, 4, 19, 0),

    # These dates currently seem ok on the distribution server; preserved here
    # in case they are convenient in the future.
    #"v14_0_rc1": datetime.datetime(2017, 9, 7, 1, 27, 0, 0),  # from EUPS HTTP server
    #"v14_0_rc2": datetime.datetime(2017, 10, 6, 22, 11, 0, 0),  # from EUPS HTTP server
    #"v14_0": datetime.datetime(2017, 10, 23, 19, 8, 15, 0),
    #"v15_0_rc1": datetime.datetime(2018, 3, 20, 22, 36, 15, 0),
    #"v15_0_rc2": datetime.datetime(2018, 3, 23, 22, 3, 0, 0),  # from EUPS HTTP server
    #"v15_0_rc3": datetime.datetime(2018, 3, 29, 21, 27, 0, 0),  # from EUPS HTTP server
    #"v15_0": datetime.datetime(2018, 4, 6, 17, 45, 43, 0),
    #"v16_0_rc1": datetime.datetime(2018, 6, 7, 17, 59, 55, 0),
    #"v16_0_rc2": datetime.datetime(2018, 6, 25, 19, 59, 8, 0),
    #"v16_0": datetime.datetime(2018, 6, 28, 20, 48, 1, 0),
    #"v17_0_rc1": datetime.datetime(2019, 2, 12, 16, 38, 9, 0),
    #"v17_0_rc2": datetime.datetime(2019, 2, 20, 18, 25, 29, 0),
    #"v17_0": datetime.datetime(2019, 2, 15, 11, 25, 19, 0),
    #"v17_0_1_rc1": datetime.datetime(2019, 3, 12, 16, 1, 44, 0),
    #"v17_0_1": datetime.datetime(2019, 2, 15, 11, 25, 19, 0),
    #"v18_0_0_rc1": datetime.datetime(2019, 6, 12, 16, 52, 1, 0),
    #"v18_0_0": datetime.datetime(2019, 7, 9, 18, 21, 5, 0),
    #"v18_1_0_rc1": datetime.datetime(2019, 7, 24, 22, 24, 22),
    #"v18_1_0": datetime.datetime(2019, 8, 8, 19, 0, 47, 0),
    #"v19_0_0_rc1": datetime.datetime(2019, 11, 19, 19, 26, 9, 0),
    #"v19_0_0": datetime.datetime(2019, 12, 5, 23, 58, 43, 0),
    #"v20_0_0.rc1": datetime.datetime(2020, 6, 5, 18, 25, 35, 0)
}
