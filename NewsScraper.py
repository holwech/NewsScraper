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
        return json.load(data_file)


def _handle_rss(company, value, count, limit):
    """If a RSS link is provided in the JSON file, this will be the first
    choice.

    Reason for this is that, RSS feeds often give more consistent and
    correct data.

    If you do not want to scrape from the RSS-feed, just leave the RSS
    attr empty in the JSON file.
    """

    fpd = fp.parse(value["rss"])
    print("Downloading articles from ", company)
    newsPaper = {"rss": value["rss"], "link": value["link"], "articles": []}
    for entry in fpd.entries:
        # Check if publish date is provided, if no the article is
        # skipped.  This is done to keep consistency in the data and to
        # keep the script from crashing.
        if hasattr(entry, "published"):
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
            newsPaper["articles"].append(article)
            print(
                "{} articles downloaded from {}, url: {}".format(
                    count, company, entry.link
                )
            )
            count = count + 1
    return count, newsPaper


def _handle_fallback(company, value, count, limit):
    """This is the fallback method if a RSS-feed link is not provided.

    It uses the python newspaper library to extract articles.

    """

    print("Building site for {}".format(company))
    paper = newspaper.build(value["link"], memoize_articles=False)
    newsPaper = {"link": value["link"], "articles": []}
    noneTypeCount = 0
    for content in paper.articles:
        if count > limit:
            break
        try:
            content.download()
            content.parse()
        except Exception as e:
            print(e)
            print("continuing...")
            continue
        # Again, for consistency, if there is no found publish date the
        # article will be skipped.
        #
        # After 10 downloaded articles from the same newspaper without
        # publish date, the company will be skipped.
        if content.publish_date is None:
            print(count, " Article has date of type None...")
            noneTypeCount = noneTypeCount + 1
            if noneTypeCount > 10:
                print("Too many noneType dates, aborting...")
                noneTypeCount = 0
                break
            count = count + 1
            continue
        article = {}
        article["title"] = content.title
        article["text"] = content.text
        article["link"] = content.url
        article["published"] = content.publish_date.isoformat()
        newsPaper["articles"].append(article)
        print(
            "{} articles downloaded from {} using newspaper, url: {}".format(
                count, company, content.url
            )
        )
        count = count + 1
        noneTypeCount = 0
    return count, newsPaper


def run(config, limit=4):
    # Iterate through each news company
    for company, value in config.items():
        count = 1
        if "rss" in value:
            count, newsPaper = _handle_rss(company, value, count, limit)
        else:
            count, newsPaper = _handle_fallback(company, value, count, limit)
        data["newspapers"][company] = newsPaper

    # Finally it saves the articles as a JSON-file.
    try:
        with open("scraped_articles.json", "w") as outfile:
            json.dump(data, outfile)
    except Exception as err:
        print(err)


def main():
    args = list(sys.argv)

    if len(args) < 2:
        sys.exit("Usage: NewsScraper.py NewsPapers.json")

    limit = 4
    if "--limit" in args:
        idx = args.index("--limit")
        limit = int(args[idx + 1])
        args = [args[i] for i in range(len(args)) if i not in (idx, idx + 1)]

    fname = args[1]
    config = parse_config(fname)
    run(config, limit=limit)


if __name__ == "__main__":
    main()
