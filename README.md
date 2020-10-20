# NewsScraper - Scrape any newspaper automatically

This is a simple python script for automatically scraping the most
recent articles from any news-site.

Just add the websites you want to scrape to `NewsPapers.json` and the
script will go through and scrape each site listed in the file.

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
  "cnn": {
    "link": "http://edition.cnn.com/"
  },
  "bbc": {
    "rss": "http://feeds.bbci.co.uk/news/rss.xml",
    "link": "http://www.bbc.com/"
  },
  "theguardian": {
    "rss": "https://www.theguardian.com/uk/rss",
    "link": "https://www.theguardian.com/international"
  },
  "breitbart": {
    "link": "http://www.breitbart.com/"
  },
  "infowars": {
    "link": "https://www.infowars.com/"
  },
  "foxnews": {
    "link": "http://www.foxnews.com/"
  },
  "nbcnews": {
    "link": "http://www.nbcnews.com/"
  },
  "washingtonpost": {
    "rss": "http://feeds.washingtonpost.com/rss/world",
    "link": "https://www.washingtonpost.com/"
  }
}
```


## Libraries

This script uses the following libraries:

https://github.com/codelucas/newspaper

https://github.com/kurtmckee/feedparser
