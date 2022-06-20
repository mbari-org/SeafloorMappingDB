import socket

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=["*"])  # Disable ALLOW_HOSTS
class BaseTestCase(StaticLiveServerTestCase):
    """
    Provides base test class which connects to the Docker
    container running Selenium.
    """

    def setUp(self):
        self.chrome = webdriver.Remote(
            command_executor="http://selenium-hub:4444/wd/hub",
            options=webdriver.ChromeOptions(),
        )
        self.chrome.implicitly_wait(10)
        self.server_url = "http://django:8001"


class HomePageTest(BaseTestCase):
    def test_home_page_open(self):
        self.chrome.get(self.server_url)
        self.assertIn("SeafloorMappingDB", self.chrome.title)
        number = self.chrome.find_element(By.ID, "num-missions").text
        self.assertEqual("5", number)

    def test_spatial_bounds_link(self):
        self.chrome.find_element(By.ID, "use_bounds").click()
        self.chrome.find_element(By.ID, "update-map").click()
        # TODO: test for map bounds in url
        self.assertIn("", self.chrome.current_url)
