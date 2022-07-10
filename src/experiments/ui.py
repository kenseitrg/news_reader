from typing import Iterable, List
from itertools import cycle
from textual.widget import Widget
from textual.reactive import Reactive
from textual.app import App
from textual import events
from textual.keys import Keys
from textual.widgets import Footer, ScrollView
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel
from rich.console import Group, RenderableType

from .feed_parser import parse_feeds

feeds = parse_feeds()


class ListItem(Widget):
    highlighted = Reactive(False)
    text = Reactive("")

    def __init__(self, text, name: str | None = None) -> None:
        super().__init__(name)
        self.text = text

    def render(self) -> Text:
        return Text(self.text, style="bold" if self.highlighted else "")


class ListView(Widget):
    idx = Reactive(0)
    has_focus: Reactive[bool] = Reactive(False)
    items: Reactive[List[ListItem]] = Reactive([])

    def __init__(self, items: List[ListItem], name: str | None = None) -> None:
        super().__init__(name)
        self.items = items
        self.name = name
        self.items[self.idx].highlighted = True

    def render(self):
        return Panel(
            Group(*self.items),
            title=self.name,
            border_style="green" if self.has_focus else "black",
        )

    def on_key(self, event: events.Key):
        if self.has_focus:
            self.process_key(event)

    def process_key(self, event: events.Key):
        if event.key == Keys.Up:
            self.items[self.idx].highlighted = False
            self.idx = max(0, self.idx - 1)
            self.items[self.idx].highlighted = True
            self.app.articles_view.update_items(self.idx)
        elif event.key == Keys.Down:
            self.items[self.idx].highlighted = False
            self.idx = min(len(self.items) - 1, self.idx + 1)
            self.items[self.idx].highlighted = True
            self.app.articles_view.update_items(self.idx)

    async def on_focus(self, event: events.Focus) -> None:
        if self.idx >= len(self.items):
            self.idx = 0
        self.items[self.idx].highlighted = True
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    async def on_enter(self, event: events.Enter) -> None:
        if self.idx >= len(self.items):
            self.idx = 0
        self.items[self.idx].highlighted = True
        self.has_focus = True

    async def on_leave(self, event: events.Leave) -> None:
        self.has_focus = False


class ArticleListView(ListView):
    idx = Reactive(0)
    has_focus: Reactive[bool] = Reactive(False)
    items: Reactive[List[ListItem]] = Reactive([])

    def update_items(self, idx):
        self.items = [ListItem(a.title) for a in feeds[idx].entries]

    def process_key(self, event: events.Key):
        if event.key == Keys.Up:
            self.items[self.idx].highlighted = False
            self.idx = max(0, self.idx - 1)
            self.items[self.idx].highlighted = True
            self.app.summary_view.text = (
                feeds[self.app.sources_view.idx].entries[self.idx].summary
            )
        elif event.key == Keys.Down:
            self.items[self.idx].highlighted = False
            self.idx = min(len(self.items) - 1, self.idx + 1)
            self.items[self.idx].highlighted = True
            self.app.summary_view.text = (
                feeds[self.app.sources_view.idx].entries[self.idx].summary
            )


class SummaryView(Widget):
    text = Reactive("str")
    has_focus: Reactive[bool] = Reactive(False)

    def __init__(self, text, name: str | None = None) -> None:
        super().__init__(name)
        self.text = text
        self.name = name

    def render(self) -> Text:
        return Panel(
            Markdown(self.text),
            title=self.name,
            border_style="green" if self.has_focus else "black",
        )


class UI(App):
    sources_view: Reactive[RenderableType] = Reactive(False)
    articles_view: Reactive[RenderableType] = Reactive(False)
    summary_view: Reactive[RenderableType] = Reactive(False)
    widget_iter: Iterable[RenderableType] = Reactive(False)

    async def on_load(self) -> None:
        await self.bind("q", "quit", "Quit")
        await self.bind("ctrl+i", "switch_focus", "Switch Focus")

    async def on_mount(self) -> None:
        sources = [ListItem(f.source) for f in feeds]
        self.sources_view = ListView(sources, name="Feed Source")
        articles = [ListItem(a.title) for a in feeds[0].entries]
        self.articles_view = ArticleListView(articles, name="Articles")
        summary = feeds[0].entries[0].summary
        self.summary_view = SummaryView(summary, name="Summary")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.sources_view, edge="left", size=30)
        await self.view.dock(
            self.articles_view,
            self.summary_view,
            edge="top",
        )
        self.widget_iter = cycle([self.sources_view, self.articles_view])
        await self.action_switch_focus()

    async def action_switch_focus(self):
        cur = next(self.widget_iter)
        await cur.focus()
