from typing import List
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown
from markdownify import markdownify as md
from .feed_parser import parse_feeds, RssEntry
from .article_reader import text_from_url

feeds = parse_feeds()
console = Console()


def get_idx(lower: int, upper: int, message: str) -> int:
    idx_raw = console.input(message)
    try:
        idx = int(idx_raw)
    except ValueError:
        console.print(Text("Invalid input"), style="red")
        return get_idx(lower, upper, message)
    if idx - 1 < lower or idx - 1 >= upper:
        console.print(Text("Index out of range"), style="red")
        return get_idx(lower, upper, message)
    else:
        return idx - 1


def prepare_table(articles: List[RssEntry]) -> Table:
    table = Table(title="Articles", show_lines=True)
    table.add_column("#")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Link")
    for i, a in enumerate(articles):
        table.add_row(str(i + 1), a.title, a.author, a.link)
    return table


def read_or_back(url: str):
    action = console.input("Press 'r' to read or any key to re-start: ")
    if action == "r":
        text = text_from_url(url)
        console.print(Panel(Markdown(md(text))))
    else:
        run()


def run():
    src = [Text(f"{i+1}. {f.source}") for i, f in enumerate(feeds)]
    console.print(Panel(Group(*src), title="Sources"))
    src_idx = get_idx(0, len(src), "Please select feed source: ")
    console.print(prepare_table(feeds[src_idx].entries))
    article_idx = get_idx(0, len(feeds[src_idx].entries), "Please select article: ")
    summary = feeds[src_idx].entries[article_idx].summary
    title = feeds[src_idx].entries[article_idx].title
    link = feeds[src_idx].entries[article_idx].link
    console.print(Panel(Markdown(md(summary)), title=title))
    read_or_back(link)
