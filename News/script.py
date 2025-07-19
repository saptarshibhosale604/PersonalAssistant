

import requests
import datetime

# ====== CONFIG ======
API_KEY = '58f7587bd332431ab356a3b02d98f3b5'  # Replace with your NewsAPI key
                                                # firefox mail: f9dye3sdg@mozmail.com
NEWS_URL = 'https://newsapi.org/v2/top-headlines'
PARAMS = {
    'language': 'en',
    'pageSize': 5,
    'sortBy': 'publishedAt',
    'apiKey': API_KEY,
}
# Use 'us' or 'gb' for country-specific; omit or use 'category=general' for global.
# ====================


def get_top_news(params):
    response = requests.get(NEWS_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get('articles', [])


def save_news_to_md(articles, label):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"Data/{timestamp}_{label}_news.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Top 5 {label.title()} News ({timestamp})\n\n")
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No Title")
            desc = article.get("description", "No Description")
            url = article.get("url", "")
            # Write to file
            f.write(f"## {i}. {title}\n")
            f.write(f"{desc}\n\n")
            f.write(f"[Read more]({url})\n\n")
            # Print to terminal
            print(f"{i}. {title}")
            print(f"   {desc}")
            print(f"   Link: {url}\n")
    print(f"✅ Saved news to {filename}")

def main():
    print("Select news type:")
    print("1. Global Top 5 News")
    print("2. India Top 5 News")
    choice = input("Enter option (1 or 2): ").strip()

    if choice == '1':
        params = {
            'language': 'en',
            'pageSize': 9,
            'sortBy': 'publishedAt',
            'apiKey': API_KEY,
        }
        label = 'global'

    elif choice == '2':
        params = {
            'language': 'en',
            'pageSize': 9,
            'country': 'in',
            'sortBy': 'publishedAt',
            'apiKey': API_KEY,
        }
        label = 'india'

    else:
        print("❌ Invalid option. Please enter 1 or 2.")
        return

    try:
        articles = get_top_news(params)
        save_news_to_md(articles, label)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()