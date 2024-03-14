import os

import pytest
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

# Monitor browser progress with: http://localhost:7900/?autoconnect=1&resize=scale&password=secret


class SeleniumTest(TestCase):
    def setUp(self):
        chrome_options = webdriver.ChromeOptions()
        print(f"Getting webdriver.Remote() instance with chrome_options")
        self.chrome = webdriver.Remote(
            command_executor="http://selenium-hub:4444/wd/hub",
            options=chrome_options,
        )
        self.chrome.implicitly_wait(10)
        # Requires that the development server is running and has the
        # missions_notes_5.json fixture loaded.  I tried to figure out how to
        # use LiveServerTestCase, but it doesn't seem to work with Selenium
        # as I get connection refused errors when using the LiveServerTestCase
        # server_url's port number on the django container.
        #
        # This would be nice to have working in GitHub Actions. Perhaps
        # setting DATABASE_URL to use the 'test_default' database will
        # make it work.
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
        print(f"POSTGRES_DB: {os.environ['POSTGRES_DB']}")
        print(f"DATABASE_URL: {os.environ['DATABASE_URL']}")
        self.assertEqual("5", number)

    @pytest.mark.django_db
    @pytest.mark.selenium
    def test_spatial_bounds_link(self):
        self.chrome.get(self.server_url)
        # Example map-bounds text: '-122.0852,36.6395,-121.7275,36.8486'
        # Crazy, now it's: '36.6395, -122.0825; 36.8486, -121.7299'
        initial_bounds = self.chrome.find_element(By.ID, "map-bounds").text
        # Transform to: "xmin=-122.0852&xmax=-121.7275&ymin=36.6395&ymax=36.8486"
        req_str = f"xmin={initial_bounds.split(';')[0].split(',')[1].strip()}&"
        req_str += f"xmax={initial_bounds.split(';')[1].split(',')[1].strip()}&"
        req_str += f"ymin={initial_bounds.split(';')[0].split(',')[0].strip()}&"
        req_str += f"ymax={initial_bounds.split(';')[1].split(',')[0].strip()}"
        self.chrome.find_element(By.ID, "use_bounds").click()
        self.chrome.find_element(By.ID, "searchbtn").click()
        self.assertIn(
            req_str,
            self.chrome.current_url,
            "Expected bounds to be that of initial 5 mission fixture.",
        )
