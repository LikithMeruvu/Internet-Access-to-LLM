from duckduckgo_search import DDGS, AsyncDDGS
from newspaper import Article
import logging

class DuckDuckGoSearcher:
    def __init__(self):
        self.ddgs = DDGS()

    def search_articles(self, keywords: str, max_results: int):
        results = self.ddgs.text(keywords, max_results=max_results)
        articles = []
        for result in results:
            url = result["href"]
            try:
                article = Article(url)
                article.download()
                article.parse()
                articles.append({
                    "title": article.title,
                    "text": article.text,
                    "url": url
                })
            except Exception as e:
                logging.error(f"Error scraping article from {url}: {e}")
        return articles

    def search_videos(self, keywords: str, max_results: int):
        results = self.ddgs.videos(
            keywords=keywords,
            region="wt-wt",
            safesearch="off",
            timelimit="Year",
            resolution="high",
            duration="medium",
            max_results=max_results,
        )
        videos = []
        for result in results:
            videos.append({
                "title": result["title"],
                "description": result["description"],
                "url": result["content"]
            })
        return videos

    async def search_images(self, keywords: str, max_results: int):
        results = await AsyncDDGS().aimages(
            keywords,
            region="wt-wt",
            safesearch="off",
            max_results=max_results,
            timelimit="Month"
        )
        images = []
        for result in results:
            images.append({
                "title": result["title"],
                "thumbnail": result["thumbnail"],
                "url": result["url"],
                "image": result["image"]
            })
        return images

    async def search_all(self, keywords: str, max_results: int, imgkey: str):
        articles = self.search_articles(keywords, max_results)
        videos = self.search_videos(imgkey, max_results)
        images = await self.search_images(imgkey, max_results)
        return articles, videos, images
