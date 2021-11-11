from typing import List
from time import sleep
import shutil
import requests
from requests.models import Response
from concurrent import futures
import os
from io import BytesIO
import uuid

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from utils import get_config


class Crawler:
    def __init__(self, headless: bool = False) -> None:
        self.config = get_config()
        self.homepage = "https://www.instagram.com/"
        self.search_template = "https://www.instagram.com/explore/tags/{}/"
        self.driver = self.make_driver(headless)
        self.total_img_num = None

    @staticmethod
    def make_driver(headeless: bool = False) -> Chrome:
        if headeless:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            driver = Chrome(
                executable_path="./chromedriver.exe", chrome_options=options
            )
            driver.execute_script(
                "Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})"
            )
            driver.execute_script(
                "Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})"
            )
            return driver

        driver = Chrome()
        driver.execute_script(
            "Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})"
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})"
        )
        return driver

    def destroy_driver(self) -> None:
        self.driver.close()
        self.driver.quit()

    def login(self) -> None:
        self.driver.get(self.homepage)

        id_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, self.config["ID_XPATH"]))
        )
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, self.config["PASSWORD_XPATH"]))
        )
        login_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, self.config["LOGIN_BUTTON_XPATH"])
            )
        )

        id_input.send_keys(self.config["ID"])
        password_input.send_keys(self.config["PASSWORD"])
        login_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, self.config["SEARCH_BAR_XPATH"]))
        )

    def search_tag(self, tag: str) -> None:
        self.driver.get(self.search_template.format(tag))
        self.tag = tag

        try:
            self.total_img_num = int(
                WebDriverWait(self.driver, 10)
                .until(
                    EC.presence_of_element_located(
                        (By.XPATH, self.config["TOTAL_IMG_NUM_XPATH"])
                    )
                )
                .text.replace(",", "")
            )
        except TimeoutException as e:
            try:
                self.total_img_num = int(
                    len(
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located(
                                (By.XPATH, self.config["POP_IMG_XPATH"])
                            )
                        )
                    )
                )
            except TimeoutException as e:
                print("Failed to find an image related to the tag.")
                self.destroy_driver()
                return None

        print(f"Found {self.total_img_num} image(s) of {tag}.")

    def __get_pop_image_urls(self) -> set:
        pop_image_urls = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, self.config["POP_IMG_XPATH"])
            )
        )
        pop_image_urls = {url.get_attribute("src") for url in pop_image_urls}

        return pop_image_urls

    def __get_recent_image_urls(self) -> set:
        recent_image_urls = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, self.config["RECENT_IMG_XPATH"])
            )
        )
        recent_image_urls = {url.get_attribute("src") for url in recent_image_urls}

        return recent_image_urls

    def __scroll_down(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)

    def get_image_urls(self, max_image: int) -> List[str]:
        image_urls = set()
        previous_length = 0

        if self.total_img_num == None:
            raise ValueError("You have to search for the tag first.")

        if self.total_img_num <= max_image:
            max_image = self.total_img_num
            print("The entered value is more than the total number of images.")

        image_urls = image_urls | self.__get_pop_image_urls()

        if self.total_img_num <= 18:
            try:
                image_urls = image_urls | self.__get_recent_image_urls()
            except TimeoutException as e:
                pass
            finally:
                current_length = len(image_urls)
                print(f"Collected {current_length} image URLs")
        else:
            while len(image_urls) <= max_image:
                image_urls = image_urls | self.__get_recent_image_urls()
                current_length = len(image_urls)

                if previous_length != current_length:
                    current_length = min(current_length, max_image)
                    print(f"Collected {current_length} image URLs")

                previous_length = current_length

                self.__scroll_down()

        if len(image_urls) > max_image:
            return list(image_urls)[:max_image]
        return list(image_urls)

    def get_image(self, url: str) -> Response:
        return requests.get(url)

    def get_images(self, urls: List[str]) -> List[Response]:
        with futures.ThreadPoolExecutor() as executor:
            images = list(executor.map(self.get_image, urls))
        return images

    def save_image(self, response: Response) -> None:
        if response.status_code == 200:
            file_name = "images/" + self.tag + "/" + uuid.uuid4().hex + ".jpg"
            with open(file_name, "wb") as f:
                shutil.copyfileobj(BytesIO(response.content), f)
            del response
            print(f"Saved {file_name}")

    def save_images(self, responses: List[Response]) -> None:
        save_dir = "images/" + self.tag
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        results = [self.save_image(response) for response in responses]
