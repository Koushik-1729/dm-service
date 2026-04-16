import re
from typing import Dict, Any, List
from urllib.parse import urljoin
from loguru import logger
import httpx
from bs4 import BeautifulSoup

from app.core.marketing_stack.outbound.external.web_scraper_port import WebScraperPort


class BeautifulSoupScraper(WebScraperPort):
    """Web scraper using httpx + BeautifulSoup implementing WebScraperPort."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        logger.info(f"Scraping URL: {url}")

        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers={"User-Agent": self.USER_AGENT},
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove scripts, styles, and nav elements for cleaner text
            for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                element.decompose()

            data = {
                "url": str(response.url),
                "title": self._get_title(soup),
                "meta_description": self._get_meta(soup, "description"),
                "meta_keywords": self._get_meta(soup, "keywords"),
                "headings": self._get_headings(soup),
                "body_text": self._get_body_text(soup),
                "images": self._get_images(soup, str(response.url)),
                "contact": self._get_contact_info(soup, response.text),
                "social_links": self._get_social_links(soup),
                "og_data": self._get_og_data(soup),
            }

            logger.info(f"Scraped {url}: title='{data['title']}', text_length={len(data['body_text'])}")
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error scraping {url}: {e.response.status_code}")
            return {"url": url, "error": f"HTTP {e.response.status_code}"}
        except httpx.TimeoutException:
            logger.error(f"Timeout scraping {url}")
            return {"url": url, "error": "Timeout"}
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {type(e).__name__}: {e}")
            return {"url": url, "error": str(e)}

    async def scrape_google_maps(self, url: str) -> Dict[str, Any]:
        logger.info(f"Scraping Google Maps: {url}")

        try:
            async with httpx.AsyncClient(
                timeout=15.0,
                follow_redirects=True,
                headers={"User-Agent": self.USER_AGENT},
            ) as client:
                response = await client.get(url)

            soup = BeautifulSoup(response.text, "html.parser")
            text = response.text

            data = {
                "url": str(response.url),
                "title": self._get_title(soup),
                "source": "google_maps",
            }

            # Try to extract structured data from JSON-LD
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    import json
                    ld_data = json.loads(script.string)
                    if isinstance(ld_data, dict):
                        data["name"] = ld_data.get("name", "")
                        data["address"] = ld_data.get("address", {})
                        data["rating"] = ld_data.get("aggregateRating", {}).get("ratingValue")
                        data["review_count"] = ld_data.get("aggregateRating", {}).get("reviewCount")
                        data["phone"] = ld_data.get("telephone", "")
                        data["category"] = ld_data.get("@type", "")
                except Exception:
                    pass

            logger.info(f"Scraped GMB: {data.get('name', 'Unknown')}")
            return data

        except Exception as e:
            logger.error(f"GMB scraping failed for {url}: {e}")
            return {"url": url, "source": "google_maps", "error": str(e)}

    def _get_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("title")
        return tag.get_text(strip=True) if tag else ""

    def _get_meta(self, soup: BeautifulSoup, name: str) -> str:
        tag = soup.find("meta", attrs={"name": name})
        if not tag:
            tag = soup.find("meta", attrs={"property": name})
        return tag.get("content", "") if tag else ""

    def _get_headings(self, soup: BeautifulSoup) -> List[str]:
        headings = []
        for tag in soup.find_all(["h1", "h2", "h3"])[:15]:
            text = tag.get_text(strip=True)
            if text and len(text) > 2:
                headings.append(text)
        return headings

    def _get_body_text(self, soup: BeautifulSoup) -> str:
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text[:5000]  # Cap at 5000 chars to avoid huge prompts

    def _get_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        images = []
        for img in soup.find_all("img", src=True)[:10]:
            src = img.get("src", "")
            if src and not src.startswith("data:"):
                full_url = urljoin(base_url, src)
                images.append(full_url)
        return images

    def _get_contact_info(self, soup: BeautifulSoup, raw_html: str) -> Dict[str, Any]:
        contact = {}

        # Phone numbers
        phone_links = soup.find_all("a", href=re.compile(r"^tel:"))
        if phone_links:
            contact["phone"] = phone_links[0].get("href", "").replace("tel:", "")

        # Email
        email_links = soup.find_all("a", href=re.compile(r"^mailto:"))
        if email_links:
            contact["email"] = email_links[0].get("href", "").replace("mailto:", "").split("?")[0]

        # Phone from text using regex
        if "phone" not in contact:
            phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,}', raw_html)
            if phone_match:
                contact["phone"] = phone_match.group().strip()

        return contact

    def _get_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        social = {}
        platforms = {
            "instagram.com": "instagram",
            "facebook.com": "facebook",
            "twitter.com": "twitter",
            "x.com": "twitter",
            "youtube.com": "youtube",
            "linkedin.com": "linkedin",
        }
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            for domain, platform in platforms.items():
                if domain in href and platform not in social:
                    social[platform] = href
        return social

    def _get_og_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        og = {}
        for tag in soup.find_all("meta", attrs={"property": re.compile(r"^og:")}):
            prop = tag.get("property", "").replace("og:", "")
            og[prop] = tag.get("content", "")
        return og
