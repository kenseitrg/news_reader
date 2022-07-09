import npyscreen
from .feed_parser import parse_feeds

feeds = parse_feeds()


class FeedList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(FeedList, self).__init__(*args, **keywords)
        self.add_handlers({"q": self.quit})

    def display_value(self, vl):
        return vl.source

    def actionHighlighted(self, act_on_this, keypress):
        self.parent.parentApp.getForm("ARTICLELIST").value = act_on_this
        self.parent.parentApp.switchForm("ARTICLELIST")

    def quit(self):
        self.parent.parentApp.switchForm(None)


class FeedListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = FeedList

    def beforeEditing(self):
        self.update_list()

    def update_list(self):
        self.wMain.values = feeds
        self.wMain.display()


class ArticleList(npyscreen.MultiLine):
    def display_value(self, vl):
        return vl.title

    def callback(self):
        value = self.values[self.cursor_line]
        self.parent.summary.value = value.summary
        self.parent.summary.display()

    def h_cursor_line_up(self, ch):
        self.cursor_line -= 1
        self.callback()
        if self.cursor_line < 0:
            if self.scroll_exit:
                self.cursor_line = 0
                self.h_exit_up(ch)
            else:
                self.cursor_line = 0

    def h_cursor_line_down(self, ch):
        self.cursor_line += 1
        self.callback()
        if self.cursor_line >= len(self.values):
            if self.scroll_exit:
                self.cursor_line = len(self.values) - 1
                self.h_exit_down(ch)
                return True
            else:
                self.cursor_line -= 1
                return True

        if self._my_widgets[self.cursor_line - self.start_display_at].task == "-more-":
            if self.slow_scroll:
                self.start_display_at += 1
            else:
                self.start_display_at = self.cursor_line


class ArticleListDisplay(npyscreen.ActionFormMinimal):
    def create(self):
        self.value = None
        y, x = self.useable_space()
        self.articles = self.add(ArticleList, max_height=y // 2)
        self.summary = self.add(npyscreen.MultiLineEdit, name="Summary", editable=False)

    def beforeEditing(self):
        if self.value:
            self.articles.values = self.value.entries
            self.summary.value = self.articles.values[0].summary
        else:
            self.articles.values = []

    def on_ok(self):
        self.parentApp.switchFormPrevious()


class UI_old(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", FeedListDisplay)
        self.addForm("ARTICLELIST", ArticleListDisplay)
