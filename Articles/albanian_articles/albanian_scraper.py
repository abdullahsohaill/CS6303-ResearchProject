import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define categories and URLs
categories = {
    "Policy": "https://kohajone.com/kategori/politike/",
    "Topicality": "https://kohajone.com/kategori/aktualitet/",
    "Sports": "https://kohajone.com/kategori/sporti/",
    "Chronical": "https://kohajone.com/kategori/kronike/",
    "Economy": "https://kohajone.com/kategori/ekonomi/",
    "Showbiz": "https://kohajone.com/kategori/showbiz/",
    "Region": "https://kohajone.com/kategori/rajoni/",
    "World": "https://kohajone.com/kategori/bota/",
}

# Function to fetch article content
def fetch_article_content(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the title from the <h1> tag
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else "No title"

        # Extract the content
        content_div = soup.find("div", class_="main-content-text")
        if not content_div:
            return {"title": title, "content": "No content", "url": article_url}
        
        paragraphs = content_div.find_all("p")
        content = " ".join(p.text.strip() for p in paragraphs if p.text.strip())

        return {"title": title, "content": content, "url": article_url}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article: {e}")
        return {"title": "Error", "content": "Error", "url": article_url}

# Function to scrape articles from a single category
def scrape_category(category_name, category_url, max_articles=150):
    articles_data = []
    page = 1
    articles_fetched = 0

    while articles_fetched < max_articles:
        try:
            # Fetch the category page
            url = f"{category_url}page/{page}/" if page > 1 else category_url
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all articles on the page
            article_div = soup.find("div", class_="grid-container")
            if not article_div:
                print(f"No articles found on page {page} of {category_name}")
                break
            
            articles = article_div.find_all("article", class_="posts-category")
            if not articles:
                print(f"No more articles to fetch in {category_name}")
                break

            # Loop through each article
            for article in articles:
                if articles_fetched >= max_articles:
                    break

                # Get article link
                link_tag = article.find("a", href=True)
                article_url = link_tag['href'] if link_tag else None
                if not article_url:
                    continue

                # Fetch article content
                article_data = fetch_article_content(article_url)
                article_data["category"] = category_name
                articles_data.append(article_data)
                articles_fetched += 1

            print(f"Fetched {articles_fetched} articles from {category_name}")
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching category page: {e}")
            break

    return articles_data

# Main function to scrape all categories and save to CSV
def scrape_all_categories(categories, max_articles=150, output_file="albanian_articles_scraped.csv"):
    all_articles = []

    for category_name, category_url in categories.items():
        print(f"Scraping category: {category_name}")
        category_articles = scrape_category(category_name, category_url, max_articles)
        all_articles.extend(category_articles)

    # Save to CSV
    df = pd.DataFrame(all_articles)
    df.to_csv(output_file, index=False)
    print(f"Saved all articles to {output_file}")

# Run the scraper
scrape_all_categories(categories, max_articles=150)
