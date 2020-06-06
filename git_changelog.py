import datetime
import dbm
import json
import os
import yaml

from collections import defaultdict
from typing import Dict, Set
from urllib.request import urlopen, HTTPError

from rubin_changelog.jira import JiraCache
from rubin_changelog.repository import Repository
from rubin_changelog.config import DEBUG, JIRA_API_URL, EUPS_PKGROOT, REPOS_YAML


def tag_key(tagname):
    """
    Convert a tagname ("w.YYYY.NN" or "w.YYYY.N") into a key for sorting.

    "w.2017.1"  -> 201701
    "w.2017.01" -> 201701
    "w.2017.10" -> 201710
    etc.
    """
    return int(tagname.split(".")[1]) * 100 + int(tagname.split(".")[2])

def print_tag(tagname, tickets):
    jira = JiraCache()
    print("<h2>New in {}</h2>".format(tagname))
    print("<ul>")
    for ticket in sorted(tickets, key=lambda x: int(x[3:])):  # Numeric sort
        summary = jira[ticket]
        pkgs = ", ".join(sorted(tickets[ticket]))
        link_text = (u"<li><a href=https://jira.lsstcorp.org/browse/"
                     u"{ticket}>{ticket}</a>: {summary} [{pkgs}]</li>")
        print(link_text.format(ticket=ticket.upper(), summary=summary, pkgs=pkgs))
    print("</ul>")

def format_output(changelog, repositories):
    # Ew, needs a proper templating engine
    print("<html>")
    print("<head><title>LSST DM Weekly Changelog</title></head>")
    print("<body>")
    print("<h1>LSST DM Weekly Changelog</h1>")

    # Always do master first if it exists
    # (It won't if there are no changes since the most recent weekly)
    if "master" in changelog:
        print_tag("master", changelog.pop("master", None))

    # Then the other tags in order
    for tag in sorted(changelog, reverse=True, key=tag_key):
        print_tag(tag, changelog[tag])

    gen_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M +00:00")
    repos = ", ".join(os.path.basename(r) for r in sorted(r.path for r in repositories))
    print("<p>Generated at {} by considering {}.</p>".format(gen_date, repos))
    print("</body>")
    print("</html>")

def generate_changelog(repositories):
    # Dict of tag -> ticket -> affected packages
    changelog =  defaultdict(lambda: defaultdict(set))
    for r in repositories:
        # Extract all tags which look like weeklies
        tags = sorted(r.tags(r"^w\.\d{4}\.\d?\d$"), reverse=True, key=tag_key)
        # Also include tickets which aren't yet in a weekly
        tags.insert(0, r.branch_name)

        for newtag, oldtag in zip(tags, tags[1:]):
            merges = (set(r.commits(newtag if newtag == r.branch_name else "refs/tags/" + newtag, merges_only=True)) -
                      set(r.commits(oldtag if oldtag == r.branch_name else "refs/tags/" + oldtag, merges_only=True)))

            for sha in merges:
                ticket = r.ticket(r.message(sha))
                if ticket:
                    if newtag == r.branch_name:
                        changelog["master"][ticket].add(os.path.basename(r.path))
                    else:
                        changelog[newtag][ticket].add(os.path.basename(r.path))
    return changelog

def get_packages_in_w_latest(pkgroot: str = EUPS_PKGROOT) -> Set[str]:
    u = urlopen(pkgroot + "/tags" + "/w_latest.list")
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

if __name__ == "__main__":
    target_dir = os.path.expanduser('~/repos')
    pkgs = get_urls_for_packages(get_packages_in_w_latest())
    repos = []
    for pkg in pkgs.values():
        repos.append(Repository.materialize(pkg['url'], target_dir, branch_name=pkg.get("ref", "master")))
    changelog = generate_changelog(repos)
    format_output(changelog, repos)
