import urwid
from .feed_parser import parse_feeds

feeds = parse_feeds()


class SourceList:
    @classmethod
    def create(cls) -> urwid.ListBox:
        body = [urwid.Text("Sources"), urwid.Divider()]
        sources = [
            urwid.AttrMap(urwid.Button(f.source), None, focus_map="reversed")
            for f in feeds
        ]
        body += sources
        log = urwid.SimpleFocusListWalker(body)
        return urwid.ListBox(log)


class UI:
    def __init__(self) -> None:
        self.loop = urwid.MainLoop(
            SourceList.create(),
            unhandled_input=self.exit,
            palette=[("reversed", "standout", "")],
        )

    def exit(self, key):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()
