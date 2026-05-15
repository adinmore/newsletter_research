import sys
from newspaper import Article, ArticleException

# Asks the user for the url of a news article they would like to scrape
print("Please provide the full url of the news article you would like to scrape:")
url = input()

# Trys to scrape newspaper article off the web and parse it for use
try:
    # Downloads and parses the news article, then extracts key information
    news_article = Article(url, language="en")
    news_article.download()
    news_article.parse()
    news_title = news_article.title
    news_text = news_article.text
except ArticleException as e:
    # If there is any issue accessing or parsing the news article, prints an error message and exits with an error code
    print(f"Error: There was an issue retrieving a news article from the provided url. {e}")
    sys.exit(1)

print(f"Title: {news_title}\n\n{news_text}\n")