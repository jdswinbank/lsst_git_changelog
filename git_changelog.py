import logging
import os

from collections import defaultdict

from rubin_changelog.eups import Eups
from rubin_changelog.repos import Repos
from rubin_changelog.repository import Repository
from rubin_changelog.config import DEBUG
from rubin_changelog.utils import tag_key
from rubin_changelog.output import format_output



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

if __name__ == "__main__":
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    target_dir = os.path.expanduser('~/repos')
    pkgs = Eups().products_for_tag("w_latest")
    repos_yaml = Repos()

    repos = {Repository.materialize(repos_yaml[pkg]['url'], target_dir,
                                    branch_name=repos_yaml[pkg].get("ref", "master"))
             for pkg in pkgs}

    changelog = generate_changelog(repos)
    format_output(changelog, repos)
