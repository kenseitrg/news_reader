from .src.feed_parser import parse_feeds

if __name__ == "__main__":
    feeds = parse_feeds()
    for feed in feeds:
        print(feed)
