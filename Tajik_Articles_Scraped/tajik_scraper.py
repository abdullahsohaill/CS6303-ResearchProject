import requests
from bs4 import BeautifulSoup
import csv

# Define categories and their URLs
categories = {
    "Parliament": "https://khovar.tj/category/parlament/",
    "Foreign Policy": "https://khovar.tj/category/foreign-policy/",
    "Security": "https://khovar.tj/category/security/",
    "Society": "https://khovar.tj/category/society/",
    "Region and World": "https://khovar.tj/category/region-world/",
    "Education": "https://khovar.tj/category/education/",
    "Culture": "https://khovar.tj/category/culture/",
}

# Add User-Agent header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

# Function to scrape articles from a single category
def scrape_articles_from_category(category_name, category_url, article_limit=50):
    articles = []  # To store scraped articles
    current_page = category_url

    while len(articles) < article_limit:
        print(f"Scraping {category_name}: {current_page}")
        response = requests.get(current_page, headers=headers)
        if response.status_code == 410:
            print(f"Page gone: {current_page}")
            break
        elif response.status_code != 200:
            print(f"Failed to fetch {current_page}: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract articles on the current page
        article_divs = soup.find_all('div', class_='article-big')
        for article_div in article_divs:
            if len(articles) >= article_limit:
                break

            try:
                # Extract title and link
                title_tag = article_div.find('h2').find('a')
                title = title_tag.text.strip()
                link = title_tag['href']

                # Extract publication date
                date_tag = article_div.find('span', class_='meta').find('span', class_='icon-text')
                date = date_tag.next_sibling.strip() if date_tag else "No Date"

                # Extract summary/description
                description_tag = article_div.find('p')
                description = description_tag.text.strip() if description_tag else "No Description"

                # Extract full content from the article's link
                content = scrape_full_article(link)

                articles.append({
                    'category': category_name,
                    'title': title,
                    'link': link,
                    'date': date,
                    'description': description,
                    'content': content
                })

            except Exception as e:
                print(f"Error extracting article: {e}")
                continue

        # Check if there's a next page
        next_page_tag = soup.find('a', class_='next page-numbers')
        if next_page_tag:
            current_page = next_page_tag['href']
        else:
            print(f"No more pages found for {category_name}.")
            break

    return articles[:article_limit]


# Function to scrape the full content of an article
def scrape_full_article(article_url):
    try:
        response = requests.get(article_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch article content: {article_url}")
            return "No Content"

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the specific div with class "content"
        content_div = soup.find('div', class_='content')
        if not content_div:
            print("No content div found")
            return "No Content"

        # Extract all <p> tags within this content div
        content = []
        p_tags = content_div.find_all('p')

        for i, p_tag in enumerate(p_tags):
            if i == 0:  # Handle the first <p> tag differently
                # Remove content inside <strong> tags
                for strong_tag in p_tag.find_all('strong'):
                    strong_tag.extract()  # Remove the <strong> tag content

                # Append the remaining text of the first <p> tag
                content.append(p_tag.get_text(strip=True))
            else:
                # For other <p> tags, extract all the text
                content.append(p_tag.get_text(strip=True))

        # Join all paragraphs into a single string
        return "\n".join(content)

    except Exception as e:
        print(f"Error fetching article content: {e}")
        return "No Content"



# Main function to scrape all categories and save to CSV
def scrape_all_categories(categories, output_file="tajik_articles_scraped.csv", article_limit=50):
    all_articles = []

    for category_name, category_url in categories.items():
        articles = scrape_articles_from_category(category_name, category_url, article_limit)
        all_articles.extend(articles)

    # Save to CSV
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['category', 'title', 'link', 'date', 'description', 'content'])
        writer.writeheader()
        writer.writerows(all_articles)

    print(f"Scraping completed. Data saved to {output_file}")


# Execute the scraper
if __name__ == "__main__":
    scrape_all_categories(categories, output_file="tajik_articles_scraped.csv", article_limit=150)
