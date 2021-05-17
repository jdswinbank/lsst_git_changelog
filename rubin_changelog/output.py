from datetime import datetime
from typing import Mapping, Set

from .eups import EupsTag
from .jira import JiraCache
from .typing import Changelog

def print_tag(
    tag: EupsTag, added: Set[str], dropped: Set[str], tickets: Mapping[str, Set[str]]
):
    print(f"<h2 id=\"{tag.name}\">{tag.name}</h2>")
    if tag.name != "master":
        print(f"Released {tag.date.strftime('%Y-%m-%d')}.")
    if not added and not dropped and not tickets:
        print("No changes in this version.")
    if added:
        print("<h3>Products added</h3>")
        print("<ul>")
        for product_name in sorted(added):
            print(f"<li>{product_name}</li>")
        print("</ul>")
    if dropped:
        print("<h3>Products removed</h3>")
        print("<ul>")
        for product_name in sorted(dropped):
            print(f"<li>{product_name}</li>")
        print("</ul>")
    if tickets:
        jira = JiraCache()
        print("<h3>Tickets merged</h3>")
        print("<ul>")
        for ticket_id, product_names in sorted(tickets.items(), key=lambda item: int(item[0][3:])):
            print(
                f"<li><a href=https://jira.lsstcorp.org/browse/"
                f"{ticket_id}>{ticket_id}</a>: {jira[ticket_id]} [{', '.join(sorted(product_names))}]</li>"
            )
        print("</ul>")


def print_changelog(changelog: Changelog, product_names: Set[str]):
    print("<html>")
    print("<head><title>Rubin Science Pipelines Changelog</title></head>")
    print("<body>")
    print("<h1>Rubin Science Pipelines Changelog</h1>")

    for tag, values in changelog.items():
        print_tag(tag, **values)

    gen_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M +00:00")
    print(
        f"<p>Generated at {gen_date} by considering {', '.join(sorted(product_names))}.</p>"
    )
    print("<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"2a18a020026f462d8839232c1cc61256\"}'></script><!-- End Cloudflare Web Analytics -->")
    print("</body>")
    print("</html>")
