from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

# Selenium Setup
driver = webdriver.Chrome()  # Ensure you have the correct path to your ChromeDriver
base_url = "https://www.prothomalo.com"

# Navigate to the 'Latest' section
driver.get(f"{base_url}/lifestyle")

# Track scraped URLs to avoid duplicates
scraped_urls = set()
articles_data = []

# Limit the number of articles to scrape
MAX_ARTICLES = 15

# CSV file setup
output_file = "scraped_articles.csv"
file_exists = os.path.exists(output_file)

try:
    while len(articles_data) < MAX_ARTICLES:
        # Wait for articles to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "left_image_right_news"))
            )
        except Exception as e:
            print("Articles did not load in time or no articles found:", e)
            break

        # Parse the current page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all("div", class_="left_image_right_news news_item wMFhj")
        
        if not articles:
            print("No articles found on the current page.")
            break

        print(f"Found {len(articles)} articles on the page.")

        # Extract data from each article
        for article in articles:
            if len(articles_data) >= MAX_ARTICLES:
                break  # Stop if we have reached the maximum number of articles

            try:
                # Extract title, link, and published time
                title_tag = article.find("h3", class_="headline-title")
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                link = title_tag.find("a", class_="title-link")['href']
                full_link = f"{base_url}{link}" if link.startswith("/") else link
                published_time_tag = article.find("time", class_="published-time")
                published_time = published_time_tag.get_text(strip=True) if published_time_tag else "Unknown Time"

                # Skip if the article has already been scraped
                if full_link in scraped_urls:
                    continue

                # Visit the article link to fetch full content
                driver.get(full_link)
                time.sleep(2)  # Allow time for the article page to load
                
                # Parse the article content
                article_soup = BeautifulSoup(driver.page_source, 'html.parser')
                content_paragraphs = article_soup.find_all("div", class_="story-element-text")
                full_content = "\n".join(
                    [p.get_text(strip=True) for p in content_paragraphs]
                )

                # Store data
                articles_data.append({
                    "title": title,
                    "link": full_link,
                    "published_time": published_time,
                    "content": full_content
                })
                scraped_urls.add(full_link)  # Mark URL as scraped

                print(f"Scraped article: {title}")

                # Return to the 'Latest' page
                driver.back()
                time.sleep(2)

            except Exception as e:
                print("Failed to scrape an article due to an error:", e)

        # Check if the "Load More" button exists and click it
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "load-more-content")
            print("Clicking 'Load More' button...")
            ActionChains(driver).move_to_element(load_more_button).click().perform()
            time.sleep(3)  # Wait for new content to load
        except Exception as e:
            print("No more articles to load or 'Load More' button not found. Stopping pagination.", e)
            break

finally:
    driver.quit()

# Save the collected articles to a CSV file
if articles_data:
    print(f"Saving {len(articles_data)} articles to {output_file}...")
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["title", "link", "published_time", "content"])
        if not file_exists:
            writer.writeheader()  # Write the header only if the file does not exist
        for article in articles_data:
            writer.writerow(article)

    print(f"Scraped {len(articles_data)} articles saved to {output_file}.")
else:
    print("No articles were scraped.")
