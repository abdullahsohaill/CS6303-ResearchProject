import pandas as pd

def replace_albanian_months(df):
    """Replaces Albanian month names in the 'publishing_date' column with English names."""
    month_replacements = {
        "Dhjetor": "December",
        "Nëntor": "November",
        "Tetor": "October",
        "Shtator": "September",
        "Gusht": "August",
        "Korrik": "July",
        "Qershor": "June",
        "Maj": "May",
    }
    
    for albanian, english in month_replacements.items():
        df['publishing_date'] = df['publishing_date'].str.replace(albanian, english, regex=False)
    
    return df


# Read the CSV file
try:
    df = pd.read_csv("albanian_articles_scraped_with_dates.csv")
except FileNotFoundError:
    print("Error: 'albanian_articles_scraped_with_dates.csv' not found.")
    exit()

# Apply the replacements
df = replace_albanian_months(df)

# Save the modified DataFrame back to the same CSV file, overwriting it.
df.to_csv("albanian_articles_scraped_with_dates.csv", index=False)
print("CSV file updated with English month names.")