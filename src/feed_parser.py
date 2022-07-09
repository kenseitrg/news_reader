from dataclasses import dataclass
from typing import List
import feedparser
from markdownify import markdownify as md
from ..config import feeds


@dataclass
class RssEntry:
    link: str
    title: str
    author: str
    summary: str


@dataclass
class RssEntryList:
    source: "str"
    entries: List[RssEntry]


def parse_feeds() -> List[RssEntryList]:
    output: List[RssEntryList] = []
    for feed in feeds.feeds:
        rss = feedparser.parse(feed.url)
        try:
            if rss.status == 200:
                rss_src = rss.feed.title
                try:
                    rss_entries = [
                        RssEntry(e.href, e.title, e.author, md(e.summary))
                        if "href" in e
                        else RssEntry(e.link, e.title, e.author, md(e.summary))
                        for e in rss.entries
                    ]
                    output.append(RssEntryList(rss_src, rss_entries))
                except:
                    pass
            else:
                print(f"Failed to parse {feed.url} with status {rss.status}")
        except AttributeError as exp:
            print(f"Parsing failed: {exp}")
    return output
