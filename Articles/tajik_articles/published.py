import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

def extract_tajik_publishing_date(url):
    """Extracts the publishing date from a given Tajik URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', class_='column9', style="width:100%;")
        if main_div:
            first_p = main_div.find('p')
            if first_p:
                strong_tag = first_p.find('strong')
                if strong_tag:
                    return strong_tag.get_text(strip=True)
                else:
                   print("  <strong> tag not found in first <p> tag")
            else:
                print("   First <p> tag not found")
        else:
             print("   <div class='column9' style='width:100%;'> not found")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return None

def process_row(row):
    """Processes a single row of the DataFrame."""
    url = row['link']
    if isinstance(url, str):
        print(f"Processing URL: {url}")
        publishing_date = extract_tajik_publishing_date(url)
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
    csv_file = "tajik_articles_scraped.csv"
    add_publishing_dates(csv_file)