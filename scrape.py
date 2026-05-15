import pandas as pd
from newspaper import Article, ArticleException


# Scrapes the news article at the link
# Code adapted from what I wrote in my policy_bridge project at News/news_analyze.py
def scrape(link):
  try:
    news_article = Article(link, language=lang)
    news_article.download()
    news_article.parse()
    return news_article.text
  except ArticleException as e:
    print(f"Error: There was an issue scraping the content at the provided link. {e}")
    return "NULL"


# Asks the user for the batch of links to scrape and the source country
file_name = input("Please enter the data file name: ")
country = input("Please enter the country data is sourced from: ")

# Sets up the language identifier
if (country.lower() == "hungary"):
  lang = "hu"
elif (country.lower() == "austria"):
  lang = "de"

# Reads raw data into a data frame
data = pd.read_csv("path" + file_name)

# Processes the content at each link
data["content"] = data["url"].apply(scrape)

# Saves a local copy of the updated sheet
save_file = file_name[:-9] + "content.xlsx"
data.to_excel(save_file, index=False)