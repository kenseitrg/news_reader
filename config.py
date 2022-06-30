from dataclasses import dataclass
from typing import List
from enum import Enum


class Lang(Enum):
    ENG = "en"
    RUS = "ru"


@dataclass
class FeedItem:
    url: str
    language: Lang


@dataclass
class FeedList:
    feeds: List[FeedItem]


urls = [
    "https://habr.com/ru/rss/best/weekly/?fl=ru",
    "https://dtf.ru/rss/all",
    "https://hnrss.org/newest?points=300",
]
langs = [Lang.RUS, Lang.RUS, Lang.ENG]

feeds = FeedList([FeedItem(url, lang) for url, lang in zip(urls, langs)])
