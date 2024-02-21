import os
import wget
import logging
from playwright.sync_api import sync_playwright


class NetEaseMusic:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def _init_js(self, page):
        with open(r"./stealth.min.js") as js_file:
            script = js_file.read()
            page.add_init_script(script)
            return page

    def _extract_song_info(self, page):
        items = page.frame(name="contentFrame").locator('TBODY tr').all()
        song_info = {}
        for item in items:
            href = item.locator('.txt a').get_attribute("href")
            title = item.locator('.txt b').get_attribute("title")

            id_index = href.find("id=")
            if id_index != -1:
                song_id = href[id_index + 3:]
                song_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"
                song_info[title] = song_url
        return song_info

    def _download_song(self, page, title, song_url, folder):
        try:
            page.goto(song_url)
            page.wait_for_timeout(1000)
            opened_url = page.url
            self.logger.info(f'Downloading {title}, link: {opened_url}')

            if not os.path.exists(folder):
                os.makedirs(folder)

            if "/404" not in opened_url:
                file_path = os.path.join(folder, f"{title}.mp3")
                wget.download(opened_url, file_path)
                self.logger.info(f'{title} download completed.')
            else:
                self.logger.warning(f'{title} does not exist.')

        except Exception as e:
            self.logger.error(f'Download of {title} failed: {e}')

    def album_download(self, url, folder):
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page = self._init_js(page)
        page.goto(url)
        page.wait_for_load_state("load")

        song_info = self._extract_song_info(page)
        for song_title, song_url in song_info.items():
            self._download_song(page, song_title, song_url, folder)

        page.close()
        p.stop()


if __name__ == "__main__":
    DOWNLOAD_FOLDER = "D:/Music"
    URL = "https://music.163.com/#/album?id=19164"
    music = NetEaseMusic()
    music.album_download(URL, DOWNLOAD_FOLDER)