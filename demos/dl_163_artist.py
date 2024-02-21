import os
import logging
import requests
import fake_useragent
from colorlog import ColoredFormatter
from playwright.sync_api import sync_playwright


class DownloadMusic:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self._configure_logging()
        self.playwright = None

    def _configure_logging(self):
        formatter = ColoredFormatter(
            fmt="%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'INFO': 'blue',
                'WARNING': 'yellow',
                'ERROR': 'red'
            }
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.INFO)

    def _create_browser_page(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()
        browser = self.playwright.chromium.launch(headless=False)
        context = browser.new_context(no_viewport=True, user_agent=fake_useragent.UserAgent().random)
        page = context.new_page()
        return page

    @staticmethod
    def _search_artist(page, name):
        Frame = page.frame(name="contentFrame")
        Frame.locator('#m-search-input').fill(name)
        page.wait_for_timeout(1000)
        page.locator('.m-schlist').is_visible(timeout=5000)
        Frame.get_by_role("link", name=name, exact=True).click()
        page.wait_for_timeout(1000)

    @staticmethod
    def _extract_song_info(page):
        items = page.frame(name="contentFrame").locator('#hotsong-list .txt').all()
        song_info = {}
        for i in items:
            href = i.locator('a').get_attribute("href")
            title = i.locator('b').get_attribute("title")

            id_index = href.find("id=")
            if id_index != -1:
                song_id = href[id_index + 3:]
                song_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"
                song_info[title] = song_url
        return song_info

    def _download_song(self, page, folder, title, song_url):
        try:
            page.goto(song_url)
            page.wait_for_timeout(1000)
            opened_url = page.url

            with requests.get(song_url, allow_redirects=True) as r:
                if "/404" not in opened_url:
                    os.makedirs(folder, exist_ok=True)
                    with open(os.path.join(folder, f"{title}.mp3"), 'wb') as f:
                        f.write(r.content)
                    self.log.info(f'{title} download completed.')
                else:
                    self.log.warning(f'{title} does not exist.')
        except Exception as e:
            self.log.error(f'Download of {title} failed: {e}.')

    def artist_download(self, url, name, folder):
        page = self._create_browser_page()
        try:
            page.goto(url)
            self._search_artist(page, name)
            song_info = self._extract_song_info(page)
            for song_title, song_url in song_info.items():
                self._download_song(page, folder, song_title, song_url)
        finally:
            page.close()
            if self.playwright:
                self.playwright.stop()


if __name__ == "__main__":
    music = DownloadMusic()
    music.artist_download(url='https://music.163.com/#/search/', name=input("Enter artist name: "), folder='D:/Music')
