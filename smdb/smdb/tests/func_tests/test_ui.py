import os

import pytest
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By


class SeleniumTest(TestCase):
    def setUp(self):
        chrome_options = webdriver.ChromeOptions()
        if os.environ.get("CI") == "true":
            chrome_options.add_argument("--headless")
            print(f"Getting webdriver.Chrome() instance")
            self.chrome = webdriver.Chrome(options=chrome_options)
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
        self.chrome.find_element(By.ID, "use_bounds").click()
        self.chrome.find_element(By.ID, "searchbtn").click()
        self.assertIn(
            r"xmin=-122.0852&xmax=-121.7275&ymin=36.6395&ymax=36.8486",
            self.chrome.current_url,
            "Expected bounds to be that of initial 5 mission fixture.",
        )
