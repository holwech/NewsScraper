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


data = {"newspapers": {}}


def parse_config(fname):
    # Loads the JSON files with news sites
    with open(fname, "r") as data_file:
        cfg = json.load(data_file)

    for company, value in cfg.items():
        if "link" not in value:
            raise ValueError(f"Configuration item {company} missing obligatory 'link'.")

    return cfg


def _handle_rss(company, value, limit):
    """If a RSS link is provided in the JSON file, this will be the first
    choice.

    Reason for this is that, RSS feeds often give more consistent and
    correct data.

    If you do not want to scrape from the RSS-feed, just leave the RSS
    attr empty in the JSON file.
    """

    count = 1
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
        article = {"link": entry.link}
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
        count += 1
    return news_paper


def _handle_fallback(company, url, limit):
    """This is the fallback method if a RSS-feed link is not provided.

    It uses the python newspaper library to extract articles.

    """

    print(f"Building site for {company}")
    try:
        paper = newspaper.build(url, memoize_articles=False)
    except:
        print("Error building newspaper, aborting...")
        return

    news_paper = {"link": url, "articles": []}
    print(f"{len(paper.articles)} articles found")

    num_articles_downloaded = 0
    error_count = 0

    for content in paper.articles:
        if num_articles_downloaded >= limit:
            break
        # After 10 articles with errors from the same newspaper, the company will be skipped.
        if error_count > 10:
            print("Too many errors for this source, aborting...")
            break

        try:
            content.download()
            content.parse()
        except Exception as err:
            error_count += 1
            print(err)
            print("continuing...")
            continue

        # For consistency, if there is no found publish date the article will be skipped.
        if content.publish_date is None or content.publish_date == '':
            print(f"Can't find article publish date, skipping...")
            error_count += 1
            continue

        article = {
            "title": content.title,
            "text": content.text,
            "link": content.url,
            "published": content.publish_date.isoformat(),
        }
        news_paper["articles"].append(article)
        num_articles_downloaded += 1
        print(
            f"{num_articles_downloaded} articles downloaded from {company} using newspaper, url: {content.url}"
        )

    return news_paper


def run(config, limit):
    """Take a config object of sites and urls, and an upper limit.

    Iterate through each news company.

    Write result to scraped_articles.json.
    """
    for i, (company, value) in enumerate(config.items()):
        print(f"NEWS SITE {i+1} OUT OF {len(config)}")
        if "rss" in value:
            news_paper = _handle_rss(company, value, limit)
        else:
            url = value["link"]
            news_paper = _handle_fallback(company, url, limit)
        data["newspapers"][company] = news_paper

        # Save collected data to file at each iteration in case of error
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

    limit = 10

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
