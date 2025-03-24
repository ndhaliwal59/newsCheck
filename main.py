import sys
from news_scraper import NewsScraper
from news_classifier import NewsClassifier

def main():
    """
    Main function that prompts for a URL, scrapes the content, and classifies it as Real or Fake news
    """
    # Create instances of our classes
    scraper = NewsScraper()
    classifier = NewsClassifier()
    
    # Get URL from user
    url = input("Enter the news article URL to analyze: ").strip()
    
    if not url:
        print("No URL provided. Exiting...")
        return
    
    # Scrape the article
    print("\nScraping article content...")
    article = scraper.scrape_article(url)
    
    if not article or not article.get('content'):
        print("Failed to extract article content. Please try a different URL.")
        return
    
    # Display article title
    print(f"\nArticle title: {article.get('title', 'No title found')}")
    
    # Get content length for reporting
    content = article.get('content', '')
    content_length = len(content)
    print(f"Content length: {content_length} characters")
    
    if content_length < 100:
        print("Warning: Article content is very short, which might affect classification accuracy.")
    
    # Classify the article
    print("\nAnalyzing article for authenticity...")
    result = classifier.predict(content)
    
    # Display result
    print("\n" + "="*50)
    print(f"ANALYSIS RESULT: This article appears to be {result} news.")
    print("="*50)
    
    # Optional - display a snippet of the content
    content_preview = content[:200] + "..." if len(content) > 200 else content
    print(f"\nContent preview:\n{content_preview}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
