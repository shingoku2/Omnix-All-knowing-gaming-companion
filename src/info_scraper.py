"""
Info Scraper Module
Scrapes game information from web sources
"""

import logging
from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfoScraper:
    """Scrapes gaming information from web sources"""

    def __init__(self, timeout: int = 10):
        """
        Initialize info scraper

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_game_info(self, game_name: str) -> Optional[Dict]:
        """
        Search for game information

        Args:
            game_name: Name of the game to search

        Returns:
            Dictionary with game information or None
        """
        try:
            # Try multiple sources
            info = self._search_igdb(game_name)
            if info:
                return info

            info = self._search_metacritic(game_name)
            if info:
                return info

            return None

        except Exception as e:
            logger.error(f"Error searching game info: {e}", exc_info=True)
            return None

    def _search_igdb(self, game_name: str) -> Optional[Dict]:
        """
        Search IGDB for game information

        Args:
            game_name: Name of the game

        Returns:
            Game information or None
        """
        try:
            url = f"https://www.igdb.com/search?query={game_name}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to extract game info from the page
            game_title = soup.find('h1', class_='game-title')
            game_description = soup.find('p', class_='game-description')

            if game_title:
                return {
                    "name": game_title.text.strip(),
                    "description": game_description.text.strip() if game_description else "No description",
                    "source": "IGDB"
                }

            return None

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout searching IGDB for {game_name}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error searching IGDB: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in IGDB search: {e}", exc_info=True)
            return None

    def _search_metacritic(self, game_name: str) -> Optional[Dict]:
        """
        Search Metacritic for game information

        Args:
            game_name: Name of the game

        Returns:
            Game information or None
        """
        try:
            url = f"https://www.metacritic.com/search/all/{game_name}/results"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to extract game info from the page
            game_result = soup.find('div', class_='result')

            if game_result:
                game_title = game_result.find('a')
                game_score = game_result.find('div', class_='metascore')

                return {
                    "name": game_title.text.strip() if game_title else "Unknown",
                    "score": game_score.text.strip() if game_score else "N/A",
                    "source": "Metacritic"
                }

            return None

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout searching Metacritic for {game_name}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error searching Metacritic: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Metacritic search: {e}", exc_info=True)
            return None

    def get_game_guides(self, game_name: str) -> List[Dict]:
        """
        Get game guides and walkthroughs

        Args:
            game_name: Name of the game

        Returns:
            List of guides
        """
        try:
            guides = []

            # Search for guides on common wikis
            wiki_sites = [
                f"https://www.gamepedia.com/{game_name.replace(' ', '_')}",
                f"https://www.fandom.com/wiki/{game_name.replace(' ', '_')}"
            ]

            for wiki_url in wiki_sites:
                try:
                    response = self.session.get(wiki_url, timeout=self.timeout)
                    if response.status_code == 200:
                        guides.append({
                            "title": f"{game_name} Guide",
                            "url": wiki_url,
                            "source": "Wiki"
                        })
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Error accessing wiki: {e}")
                    continue

            return guides

        except Exception as e:
            logger.error(f"Error getting game guides: {e}", exc_info=True)
            return []

    def close(self):
        """Close the session"""
        try:
            self.session.close()
            logger.info("InfoScraper session closed")
        except Exception as e:
            logger.error(f"Error closing session: {e}")


if __name__ == "__main__":
    scraper = InfoScraper()

    # Test game info search
    game_info = scraper.search_game_info("Elden Ring")
    if game_info:
        print(f"Game: {game_info}")
    else:
        print("No game info found")

    # Test guide search
    guides = scraper.get_game_guides("Elden Ring")
    if guides:
        print(f"Guides found: {len(guides)}")
        for guide in guides:
            print(f"  - {guide['title']}: {guide['url']}")

    scraper.close()
