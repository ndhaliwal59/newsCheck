import requests
from bs4 import BeautifulSoup
import random
import re
import time
from urllib.parse import urlparse
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NewsScraper:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
    ]

    NEWS_SITES = {
        'foxnews.com': {
            'title_selectors': ['h1.headline', 'h1.title', 'h1'],
            'content_selectors': ['div.article-body', 'div.article-content', 'article.story'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'embed', 'byline']
        },
        'cnn.com': {
            'title_selectors': ['h1.pg-headline', 'h1.Article__title', 'h1'],
            'content_selectors': ['div.Article__body', 'div.article__content', 'section.body-text'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['zn-body__paragraph--pull-quote', 'el__embedded', 'ad']
        },
        'msnbc.com': {
            'title_selectors': ['h1.article-header__title', 'h1.title', 'h1'],
            'content_selectors': ['div.article-body', 'div.article-body__content', 'div.body'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'widget']
        },
        'abcnews.go.com': {
            'title_selectors': ['h1.Article__Headline', 'h1.headline', 'h1'],
            'content_selectors': ['div.Article__Content', 'div.article-copy', 'article'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'embed']
        },
        'nbcnews.com': {
            'title_selectors': ['h1.article-hero__headline', 'h1.headline', 'h1'],
            'content_selectors': ['div.article-body', 'div.body', 'article'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'inline-video']
        },
        'cbsnews.com': {
            'title_selectors': ['h1.content__title', 'h1.title', 'h1'],
            'content_selectors': ['div.content__body', 'section.content__body', 'article'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'embed']
        },
        'weather.com': {
            'title_selectors': ['h1.hero-title', 'h1.title', 'h1'],
            'content_selectors': ['div.article-body', 'div.body-content', 'article'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'embed']
        },
        'espn.com': {
            'title_selectors': ['h1.article-header', 'h1.headline', 'h1'],
            'content_selectors': ['div.article-body', 'div.story-container', 'article'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'embed']
        },
        'foxbusiness.com': {
            'title_selectors': ['h1.headline', 'h1.title', 'h1'],
            'content_selectors': ['div.article-body', 'div.article-content', 'article'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'embed']
        },
        'bloomberg.com': {
            'title_selectors': ['h1.lede-text-v2__hed', 'h1.headline', 'h1'],
            'content_selectors': ['div.body-copy-v2', 'div.body-content', 'article'],
            'paragraph_selectors': ['p', 'h2', 'h3'],
            'exclude_classes': ['ad', 'related', 'embed']
        }
    }

    GENERIC_SELECTORS = {
        'title_selectors': ['h1.article-title', 'h1.headline', 'h1.title', 'h1'],
        'content_selectors': [
            'article', 
            'main article',
            'div.article-content', 
            'div.story-content', 
            'div.post-content',
            'div.entry-content',
            'div.content',
            'main'
        ],
        'paragraph_selectors': ['p', 'h2', 'h3', 'h4'],
        'exclude_classes': [
            'ad', 'ads', 'advertisement', 
            'sidebar', 'footer', 'header', 'nav', 'menu',
            'related', 'recommended', 'popular',
            'share', 'social', 'comments', 'widget', 
            'promo', 'newsletter', 'subscribe'
        ]
    }

    def __init__(self):
        self.site_config = self.GENERIC_SELECTORS

    def get_random_user_agent(self):
        return random.choice(self.USER_AGENTS)

    def clean_text(self, text):
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text).strip()
        patterns_to_remove = [
            r'by\s.+?(\s|$)',
            r'follow\s+(us|me)\s+on',
            r'sign up for our (newsletter|emails)',
            r'copyright ©',
            r'all rights reserved',
            r'terms of (use|service)',
        ]
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def find_element(self, soup, selectors):
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element
            except:
                pass
            if '.' in selector and not selector.startswith('.'):
                tag, class_name = selector.split('.', 1)
                element = soup.find(tag, class_=class_name)
            elif '#' in selector and not selector.startswith('#'):
                tag, id_name = selector.split('#', 1)
                element = soup.find(tag, id=id_name)
            else:
                element = soup.find(selector)
            if element:
                return element
        return None

    def extract_article(self, soup, base_url):
        article = {
            'title': '',
            'content': ''
        }
        title_element = self.find_element(soup, self.site_config['title_selectors'])
        if title_element:
            article['title'] = self.clean_text(title_element.get_text())
        content_div = None
        for selector in self.site_config['content_selectors']:
            try:
                content_div = soup.select_one(selector)
                if content_div:
                    break
            except:
                pass
        if not content_div:
            content_div = soup.find('article') or soup.find('main') or soup.find('body')
        paragraphs = []
        if content_div:
            for tag in self.site_config['paragraph_selectors']:
                for element in content_div.find_all(tag):
                    should_exclude = False
                    if element.get('class'):
                        element_classes = ' '.join(element.get('class')).lower()
                        if any(exclude_class in element_classes for exclude_class in self.site_config['exclude_classes']):
                            should_exclude = True
                    if not should_exclude:
                        cleaned_text = self.clean_text(element.get_text(strip=True))
                        if cleaned_text and len(cleaned_text) > 20:
                            paragraphs.append(cleaned_text)
        if not paragraphs:
            for p in soup.find_all('p'):
                text = self.clean_text(p.get_text())
                if text and len(text) > 40:
                    paragraphs.append(text)
        article['content'] = ' '.join(paragraphs)
        return article

    def extract_with_bs4(self, url):
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Upgrade-Insecure-Requests': '1',
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            base_tag = soup.find('base')
            base_url = base_tag['href'] if base_tag and 'href' in base_tag.attrs else url
            return self.extract_article(soup, base_url)
        except Exception as e:
            print(f"Error during request: {e}")
            return None

    def extract_with_selenium(self, url, use_undetected=True):
        driver = None
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument(f"--user-agent={self.get_random_user_agent()}")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            if use_undetected:
                try:
                    driver = uc.Chrome(options=options)
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                except Exception as e:
                    print(f"Undetected ChromeDriver failed: {e}")
                    return self.extract_with_selenium(url, use_undetected=False)
            else:
                driver = webdriver.Chrome(options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "p"))
                    )
                except:
                    time.sleep(3)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            return self.extract_article(soup, url)
        except Exception as e:
            print(f"Error using Selenium: {e}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def scrape_article(self, url):
        print(f"Scraping article from: {url}")
        domain = urlparse(url).netloc.lower()
        self.site_config = self.NEWS_SITES.get(domain, self.GENERIC_SELECTORS)
        article_content = self.extract_with_bs4(url)
        if not article_content or not article_content.get('content') or len(article_content.get('content', '')) < 100:
            print("Basic scraper couldn't extract content, falling back to Selenium...")
            article_content = self.extract_with_selenium(url)
        return article_content
