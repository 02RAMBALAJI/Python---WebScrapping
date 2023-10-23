import logging
import dateparser

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import Remote as RemoteDriver
from datetime import datetime


class YtWebService:
    url: str
    web_driver: RemoteDriver
    web_driver_service: ChromeService

    def __init__(self, channel_url) -> None:
        self.url = channel_url

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        self.web_driver_service = ChromeService("./chromedriver")
        self.web_driver_service.start()

        self.web_driver = RemoteDriver(
            self.web_driver_service.service_url, options=chrome_options
        )

    def __enter__(self):
        self.web_driver.get(self.url)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value:
            logging.exception(exc_traceback)
        self.web_driver.close()
        self.web_driver.quit()
        self.web_driver_service.stop()


def extract_video_metadata(video_card):
    # Returns video ID and upload time
    video_id = video_card.find_element(By.CSS_SELECTOR, "a#video-title-link").get_attribute("href")
    upload_time = video_card.find_elements(By.CSS_SELECTOR, "div#metadata-line > span")[1].get_attribute("textContent")
    upload_time = dateparser.parse(upload_time, settings={'RELATIVE_BASE': datetime.now()})
    return video_id,upload_time


def get_video_metrics(channel_url, start_date, end_date):
    metrics = {}
    with YtWebService(channel_url) as service:
        cards = service.web_driver.find_elements(By.CSS_SELECTOR, 
            "ytd-rich-item-renderer"
        )

        for card in cards:
            video_id,upload_time = extract_video_metadata(card)
            if(upload_time < start_date and upload_time > end_date):
                if not metrics.get(upload_time.date()):
                    metrics.update({upload_time.date(): []})
                metrics[upload_time.date()].append(video_id)
    return metrics


if __name__ == "__main__":
    start_date = datetime.now()
    end_date = datetime(2023, 5, 22)
    # start_date = datetime(2023, 8, 8)
    # end_date = datetime(2023, 5, 22)

    get_video_metrics("https://www.youtube.com/@tseries/videos", start_date, end_date)
    pass