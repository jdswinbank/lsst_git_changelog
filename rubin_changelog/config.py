import os

DEBUG = False
JIRA_API_URL = "https://jira.lsstcorp.org/rest/api/2"
EUPS_PKGROOT = "https://eups.lsst.codes/stack/src/"
REPOS_YAML = "https://raw.githubusercontent.com/lsst/repos/master/etc/repos.yaml"
TARGET_DIR = os.path.expanduser("~/repos")
TICKET_CACHE = os.path.join(TARGET_DIR, "ticket.cache")
PRODUCT_SKIPLIST = ["boost", "galsim", "mariadb", "mariadbclient", "qserv_testdata", "sims_skybrightness_data"]
