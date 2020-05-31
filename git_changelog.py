from collections import defaultdict
from urllib.request import urlopen, HTTPError

import datetime
import dbm
import glob
import json
import os
import re
import subprocess

DEBUG = False
GIT_EXEC = "/usr/bin/git"
GIT_LFS_EXEC = "/software/lsstsw/stack/python/current/envs/lsst-scipipe/bin/git-lfs"
JIRA_API_URL = "https://jira.lsstcorp.org/rest/api/2"

# Populated by looking at https://sw.lsstcorp.org/eupspkg/tags/w_2017_8.list,
# excluding ndarray and fftw since they don't appear to be receiving regular
# weekly tags (for reasons known, presumably, to SQuaRE).
REPOSITORIES = glob.glob("/ssd/swinbank/src/*")

class Repository(object):
    def __init__(self, path):
        self.path = path

    def __call_git(self, *args):
        to_exec = [GIT_EXEC] + list(args)

        # Make sure that git-lfs exists on the PATH.
        # (It doesn't by default on lsst-dev01)
        env = os.environ.copy()
        env['PATH'] = "%s:%s" % (os.path.dirname(GIT_LFS_EXEC), env["PATH"])

        if DEBUG:
            print(to_exec)
            print(env['PATH'])
        return subprocess.check_output(to_exec, cwd=self.path, env=env)

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

    def branch_name(self):
        branches = [br.strip("* ") for br in
                    self.__call_git("branch").split('\n')
                    if br]
        if "lsst-dev" in branches:
            return "lsst-dev"
        else:
            return "master"

    @staticmethod
    def ticket(message):
        try:
            return re.search(r"(DM-\d+)", message, re.IGNORECASE).group(1)
        except AttributeError:
            if DEBUG:
                print(message)


def get_ticket_summary(ticket):
    dbname = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "ticket.cache")
    # Context manager in Py3, but not 2, apparently
    db = dbm.open(dbname, "c")
    try:
        if ticket not in db:
            url = JIRA_API_URL + "/issue/" + ticket + "?fields=summary"
            if DEBUG:
                print(url)
            db[ticket] = json.load(urlopen(url))['fields']['summary'].encode("utf-8")
        # json gives us a unicode string, which we need to encode for storing
        # in the database, then decode again when we load it.
        return db[ticket].decode("utf-8")
    except HTTPError:
            return ("Ticket description not available")
    finally:
        db.close()

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
    print("<h2>New in {}</h2>".format(tagname))
    print("<ul>")
    for ticket in sorted(tickets, key=lambda x: int(x[3:])):  # Numeric sort
        summary = get_ticket_summary(ticket)
        pkgs = ", ".join(sorted(tickets[ticket]))
        link_text = (u"<li><a href=https://jira.lsstcorp.org/browse/"
                     u"{ticket}>{ticket}</a>: {summary} [{pkgs}]</li>")
        print(link_text.format(ticket=ticket.upper(), summary=summary, pkgs=pkgs)
                       .encode("utf-8"))
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
    repos = ", ".join(os.path.basename(r) for r in sorted(repositories))
    print("<p>Generated at {} by considering {}.</p>".format(gen_date, repos))
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
        tags = sorted(r.tags("^w\.\d{4}\.\d?\d$"), reverse=True, key=tag_key)
        # Also include tickets which aren't yet in a weekly
        tags.insert(0, r.branch_name())

        for newtag, oldtag in zip(tags, tags[1:]):
            merges = (set(r.commits(newtag, merges_only=True)) -
                      set(r.commits(oldtag, merges_only=True)))

            for sha in merges:
                ticket = r.ticket(r.message(sha))
                if ticket:
                    if newtag == r.branch_name():
                        changelog["master"][ticket].add(os.path.basename(repository))
                    else:
                        changelog[newtag][ticket].add(os.path.basename(repository))
    return changelog


if __name__ == "__main__":
    changelog = generate_changelog(REPOSITORIES)
    format_output(changelog, REPOSITORIES)
