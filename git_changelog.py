from __future__ import print_function
from collections import defaultdict
import datetime
import glob
import json
import os
import re
import subprocess
from urllib2 import urlopen

DEBUG = False
GIT_EXEC = "/usr/bin/git"
REPOSITORIES = glob.glob("/ssd/swinbank/src/*")  # Everything in w_2017_8
JIRA_API_URL = "https://jira.lsstcorp.org/rest/api/2"

class Repository(object):
    def __init__(self, path):
        self.path = path

    def __call_git(self, *args):
        to_exec = [GIT_EXEC] + list(args)
        if DEBUG:
            print(to_exec)
        return subprocess.check_output(to_exec, cwd=self.path)

    def commits(self, reachable_from=None, merges_only=False):
        args = ["log", "--pretty=format:%H"]
        if reachable_from:
            args.append(reachable_from)
        if merges_only:
            args.append("--merges")
        return self.__call_git(*args).split()

    def message(self, commit_hash):
        return self.__call_git("show", commit_hash, "--pretty=format:%s")

    def tags(self, pattern=r".*"):
        return [tag for tag in self.__call_git("tag").split()
                if re.search(pattern, tag)]

    def update(self):
        return self.__call_git("pull")

    @staticmethod
    def ticket(message):
        try:
            return re.search(r"(DM-\d+)", message, re.IGNORECASE).group(1)
        except AttributeError:
            if DEBUG:
                print(message)


def get_ticket_summary(ticket):
    url = JIRA_API_URL + "/issue/" + ticket + "?fields=summary"
    if DEBUG:
        print(url)
    j = json.load(urlopen(url))
    return j['fields']['summary']

def print_tag(tagname, tickets):
    print("<h2>New in {}</h2>".format(tagname))
    print("<ul>")
    for ticket in sorted(tickets, key=lambda x: int(x[3:])):  # Numeric sort
        summary = get_ticket_summary(ticket)
        pkgs = ", ".join(sorted(tickets[ticket]))
        link_text = (u"<li><a href=https://jira.lsstcorp.org/browse/"
                     u"{ticket}>{ticket}</a>: {summary} [{pkgs}]</li>")
        print(link_text.format(ticket=ticket, summary=summary, pkgs=pkgs)
                       .encode("utf-8"))
    print("</ul>")

def format_output(changelog):
    # Ew, needs a proper templating engine
    print("<html>")
    print("<body>")
    print("<h1>LSST DM Weekly Changelog</h1>")

    # Always do master first
    print_tag("master", changelog.pop("master"))

    # Then the other tags in order
    for tag in sorted(changelog, reverse=True):
        print_tag(tag, changelog[tag])

    gen_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M +00:00")
    print("<p>Generated {}.</p>".format(gen_date))
    print("</body>")
    print("</html>")

def generate_changelog(repositories):
    # Dict of tag -> ticket -> affected packages
    changelog =  defaultdict(lambda: defaultdict(set))
    for repository in repositories:
        if DEBUG:
            print(repository)
        r = Repository(repository)
        r.update()

        # Extract all tags which look like weeklies
        tags = sorted(r.tags("w\.\d{4}"), reverse=True)
        # Also include tickets which aren't yet in a weekly
        tags.insert(0, "master")

        for newtag, oldtag in zip(tags, tags[1:]):
            merges = (set(r.commits(newtag, merges_only=True)) -
                      set(r.commits(oldtag, merges_only=True)))

            for sha in merges:
                ticket = r.ticket(r.message(sha))
                if ticket:
                    changelog[newtag][ticket].add(os.path.basename(repository))
    return changelog


if __name__ == "__main__":
    changelog = generate_changelog(REPOSITORIES)
    format_output(changelog)
