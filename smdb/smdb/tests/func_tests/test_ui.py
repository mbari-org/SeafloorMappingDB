import os

import pytest
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTest(TestCase):
    def setUp(self):
        chrome_options = webdriver.ChromeOptions()
        if os.environ.get("CI") == "true":
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            print(f"Getting webdriver.Chrome() instance")
            chrome_options.binary_location = "/usr/bin/google-chrome"
            self.chrome = webdriver.Chrome(
                service=ChromeService(executable_path="/usr/local/bin/chromedriver"),
                options=chrome_options,
            )
        else:
            print(f"Getting webdriver.Remote() instance with chrome_options")
            self.chrome = webdriver.Remote(
                command_executor="http://selenium-hub:4444/wd/hub",
                options=chrome_options,
            )
        self.chrome.implicitly_wait(10)
        self.server_url = "http://django:8001"

    def tearDown(self):
        self.chrome.quit()

    @pytest.mark.django_db
    @pytest.mark.selenium
    def test_visit_site_with_chrome(self):
        print(f"Lauching chrome browser at: {self.server_url}")
        self.chrome.get(self.server_url)
        self.assertIn("SeafloorMappingDB", self.chrome.title)
        number = self.chrome.find_element(By.ID, "num-missions").text
        self.assertEqual("5", number)

    @pytest.mark.django_db
    @pytest.mark.selenium
    def test_spatial_bounds_link(self):
        self.chrome.get(self.server_url)
        # Example map-bounds text: '-122.0852,36.6395,-121.7275,36.8486'
        initial_bounds = self.chrome.find_element(By.ID, "map-bounds").text
        # Transform to: "xmin=-122.0852&xmax=-121.7275&ymin=36.6395&ymax=36.8486"
        req_str = f"xmin={initial_bounds.split(',')[0]}&"
        req_str += f"xmax={initial_bounds.split(',')[2]}&"
        req_str += f"ymin={initial_bounds.split(',')[1]}&"
        req_str += f"ymax={initial_bounds.split(',')[3]}"
        self.chrome.find_element(By.ID, "use_bounds").click()
        self.chrome.find_element(By.ID, "searchbtn").click()
        self.assertIn(
            req_str,
            self.chrome.current_url,
            "Expected bounds to be that of initial 5 mission fixture.",
        )
