import datetime
import os

from .jira import JiraCache
from .utils import tag_key


def print_tag(tagname, tickets) -> None:
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

def format_output(changelog, repositories) -> None:
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
