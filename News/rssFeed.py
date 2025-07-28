import feedparser
from datetime import datetime

def rss_to_markdown(feed_url, max_items=5):
    feed = feedparser.parse(feed_url)
    markdown = f"# {feed.feed.get('title', 'Feed')}\n\n"
    for entry in feed.entries[:max_items]:
        title = entry.get('title', 'No Title')
        link = entry.get('link', '#')
        desc = entry.get('description', '')[:200].replace('\n', ' ')
        markdown += f"## [{title}]({link})\n"
        if desc:
            markdown += f"{desc}...\n\n"
    return markdown

def save_markdown_to_file(content, prefix="rss_feed"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Data/{prefix}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Markdown saved to {filename}")

if __name__ == '__main__':
    # Replace this URL with any RSS feed URL you want
    feed_url = "https://www.newscientist.com/feed/home"    
    markdown_content = rss_to_markdown(feed_url, max_items=5)
    
    # Print markdown content to console
    print(markdown_content)
    
    # Save markdown content to a timestamped file
    save_markdown_to_file(markdown_content, prefix="rss_feed")

