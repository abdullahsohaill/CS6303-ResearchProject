import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor

def extract_publishing_date(url):
    """Extracts the publishing date from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        date_div = soup.find('div', class_='single-post-date')
        if date_div:
            date_text = date_div.get_text(strip=True).strip()
            parts = date_text.split(' ')
            date = " ".join(parts[-4:])
            if len(parts) >= 4:
                return date
            else:
                print("Date is not in correct format")
                return None
        else:
            print("   <div class='single-post-date'> not found")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return None

def process_row(row):
    """Processes a single row of the DataFrame."""
    url = row['url']
    if isinstance(url, str):
        print(f"Processing URL: {url}")
        publishing_date = extract_publishing_date(url)
        return publishing_date, row.name
    else:
        print(f"Skipping row due to invalid URL format")
        return None, row.name

def add_publishing_dates(csv_filepath, max_workers=10):
    """Adds the 'publishing_date' column to a CSV file using multithreading."""
    df = pd.read_csv(csv_filepath)
    df['publishing_date'] = None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_row, row) for _, row in df.iterrows()]
        
        for future in futures:
            result, index = future.result()
            if result:
                df.at[index, 'publishing_date'] = result


    output_csv_path = csv_filepath.replace(".csv", "_with_dates.csv")
    df.to_csv(output_csv_path, index=False)
    print(f"Successfully saved the new CSV to: {output_csv_path}")

if __name__ == "__main__":
    csv_file = "albanian_articles_scraped.csv"
    add_publishing_dates(csv_file)