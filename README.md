# NewsScraper - Scrape any newspaper automatically

This is a simple python script for automatically scraping the most
recent articles from any news-site.

Just add the websites you want to scrape to `NewsPapers.json` and the
script will go through and scrape each site listed in the file.

This repository was originally created as part of [this tutorial](https://holwech.github.io/blog/Automatic-news-scraper/).

Thanks to [Pål Grønås Drange](https://github.com/pgdr) for his contributions to the repository.

## Installing

You need to download the content of this repository, then run

```
pip install -r requirements.txt
```

## Usage

Simply run `python newsscraper.py NewsPapers.json`.

The `NewsPapers.json` file should be a JSON file like this:

```json
{
  "bbc": {
    "rss": "http://feeds.bbci.co.uk/news/rss.xml",
    "link": "http://www.bbc.com/"
  },
  "breitbart": {
    "link": "http://www.breitbart.com/"
  },
  "cnn": {
    "rss": "http://rss.cnn.com/rss/edition.rss",
    "link": "http://edition.cnn.com/"
  },
  "foxnews": {
    "rss": "http://feeds.foxnews.com/foxnews/latest",
    "link": "http://www.foxnews.com/"
  },
  "nytimes_frontpage": {
    "link": "https://nytimes.com/",
    "rss": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
  },
  "nytimes_international": {
    "link": "https://nytimes.com/",
    "rss": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
  },
  "theguardian": {
    "rss": "https://www.theguardian.com/uk/rss",
    "link": "https://www.theguardian.com/international"
  },
  "washingtonpost": {
    "rss": "http://feeds.washingtonpost.com/rss/world",
    "link": "https://www.washingtonpost.com/"
  },
  "wsj": {
    "rss": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "link": "https://www.wsj.com"
  }
}
```


## Libraries

This script uses the following libraries:

https://github.com/codelucas/newspaper

https://github.com/kurtmckee/feedparser
