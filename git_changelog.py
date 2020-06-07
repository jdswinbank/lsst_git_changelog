import datetime
import logging
import os

from collections import defaultdict
from typing import Dict, List

from rubin_changelog.config import DEBUG, TARGET_DIR
from rubin_changelog.eups import Eups, EupsTag
from rubin_changelog.jira import JiraCache
from rubin_changelog.output import format_output
from rubin_changelog.products import Products
from rubin_changelog.repos_yaml import ReposYaml
from rubin_changelog.repository import Repository
from rubin_changelog.utils import tag_key



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

def print_tag(tag: EupsTag, added: List[str], dropped: List[str], tickets: Dict[str, List[str]]):
    print(f"<h2>{tag.name}</h2>")
    if tag.date:
        print(f"Released {tag.date}.")
    if not added and not dropped and not tickets:
        print("No changes in this version.")
    if added:
        print("<h3>Products added</h3>")
        print("<ul>")
        for product_name in added:
            print(f"<li>{product_name}</li>")
        print("</ul>")
    if dropped:
        print("<h3>Products removed</h3>")
        print("<ul>")
        for product_name in dropped:
            print(f"<li>{product_name}</li>")
        print("</ul>")
    if tickets:
        jira = JiraCache()
        print("<h3>Tickets merged</h3>")
        print("<ul>")
        for ticket_id, products in tickets.items():
            print(f"<li><a href=https://jira.lsstcorp.org/browse/"
                  f"{ticket_id}>{ticket_id}</a>: {jira[ticket_id]} [{', '.join(products)}]</li>")
        print("</ul>")




def walk_tags(eups):#, repos):
    print("<html>")
    print("<head><title>Rubin Science Pipelines Weekly Changelog</title></head>")
    print("<body>")
    print("<h1>Rubin Science Pipelines Weekly Changelog</h1>")
    products = Products()
    tags = sorted(eups.values(), reverse=True)
    tags.insert(0, EupsTag("master", None, tags[0].products))
    for new_tag, old_tag in zip(tags, tags[1:]):
        added = set(new_tag.products) - set(old_tag.products)
        dropped = set(old_tag.products) - set(new_tag.products)
        tickets = defaultdict(list)
        for product_name in set(new_tag.products) & set(old_tag.products):
            try:
                product = products[product_name]
            except KeyError:
                logging.debug(f"Skipping ticket list on {product_name} (probably skiplisted)")
                continue
            old_ref_name = f"refs/tags/{old_tag.name.replace('_', '.')}"
            new_ref_name = f"refs/tags/{new_tag.name.replace('_', '.')}" if new_tag.name != "master" else products[product_name].branch_name
            merges = products[product_name].merges_between(old_ref_name, new_ref_name)
            for sha in merges:
                ticket = products[product_name].ticket(products[product_name].message(sha))
                if ticket:
                    tickets[ticket].append(product_name)
        print_tag(new_tag, added, dropped, tickets)

    gen_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M +00:00")
    print(f"<p>Generated at {gen_date} by considering {', '.join(eups.all_products)}.</p>")
    print("</body>")
    print("<html>")




if __name__ == "__main__":
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    eups = Eups(pattern="w_20")
    walk_tags(eups)
