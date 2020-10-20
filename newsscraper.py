"""A script for scraping news sites and writing latest articles to
json.
"""

import sys
import json
from time import mktime
from datetime import datetime

import feedparser as fp
import newspaper
from newspaper import Article


data = {}
data["newspapers"] = {}


def parse_config(fname):
    # Loads the JSON files with news sites
    with open(fname, "r") as data_file:
        cfg = json.load(data_file)

    for company, value in cfg.items():
        if "link" not in value:
            raise ValueError(f"Configuration item {company} missing obligatory 'link'.")

    return cfg


def _handle_rss(company, value, count, limit):
    """If a RSS link is provided in the JSON file, this will be the first
    choice.

    Reason for this is that, RSS feeds often give more consistent and
    correct data.

    If you do not want to scrape from the RSS-feed, just leave the RSS
    attr empty in the JSON file.
    """

    fpd = fp.parse(value["rss"])
    print(f"Downloading articles from {company}")
    news_paper = {"rss": value["rss"], "link": value["link"], "articles": []}
    for entry in fpd.entries:
        # Check if publish date is provided, if no the article is
        # skipped.  This is done to keep consistency in the data and to
        # keep the script from crashing.
        if not hasattr(entry, "published"):
            continue
        if count > limit:
            break
        article = {}
        article["link"] = entry.link
        date = entry.published_parsed
        article["published"] = datetime.fromtimestamp(mktime(date)).isoformat()
        try:
            content = Article(entry.link)
            content.download()
            content.parse()
        except Exception as err:
            # If the download for some reason fails (ex. 404) the
            # script will continue downloading the next article.
            print(err)
            print("continuing...")
            continue
        article["title"] = content.title
        article["text"] = content.text
        news_paper["articles"].append(article)
        print(f"{count} articles downloaded from {company}, url: {entry.link}")
        count = count + 1
    return count, news_paper


def _handle_fallback(company, value, count, limit):
    """This is the fallback method if a RSS-feed link is not provided.

    It uses the python newspaper library to extract articles.

    """

    print(f"Building site for {company}")
    paper = newspaper.build(value["link"], memoize_articles=False)
    news_paper = {"link": value["link"], "articles": []}
    none_type_count = 0
    for content in paper.articles:
        if count > limit:
            break
        try:
            content.download()
            content.parse()
        except Exception as err:
            print(err)
            print("continuing...")
            continue
        # Again, for consistency, if there is no found publish date the
        # article will be skipped.
        #
        # After 10 downloaded articles from the same newspaper without
        # publish date, the company will be skipped.
        if content.publish_date is None:
            print(f"{count} Article has date of type None...")
            none_type_count = none_type_count + 1
            if none_type_count > 10:
                print("Too many noneType dates, aborting...")
                none_type_count = 0
                break
            count = count + 1
            continue
        article = {
            "title": content.title,
            "text": content.text,
            "link": content.url,
            "published": content.publish_date.isoformat(),
        }
        news_paper["articles"].append(article)
        print(
            f"{count} articles downloaded from {company} using newspaper, url: {content.url}"
        )
        count = count + 1
        none_type_count = 0
    return count, news_paper


def run(config, limit=4):
    """Take a config object of sites and urls, and an upper limit.

    Iterate through each news company.

    Write result to scraped_articles.json.
    """
    for company, value in config.items():
        count = 1
        if "rss" in value:
            count, news_paper = _handle_rss(company, value, count, limit)
        else:
            count, news_paper = _handle_fallback(company, value, count, limit)
        data["newspapers"][company] = news_paper

    # Finally it saves the articles as a JSON-file.
    try:
        with open("scraped_articles.json", "w") as outfile:
            json.dump(data, outfile, indent=2)
    except Exception as err:
        print(err)


def main():
    """News site scraper.

    Takes a command line argument containing json.
    """

    args = list(sys.argv)

    if len(args) < 2:
        sys.exit("Usage: newsscraper.py NewsPapers.json")

    limit = 4
    if "--limit" in args:
        idx = args.index("--limit")
        limit = int(args[idx + 1])
        args = [args[i] for i in range(len(args)) if i not in (idx, idx + 1)]

    fname = args[1]
    try:
        config = parse_config(fname)
    except Exception as err:
        sys.exit(err)
    run(config, limit=limit)


if __name__ == "__main__":
    main()
