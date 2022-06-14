import socket
import sys

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, override_settings, tag
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=["*"])  # Disable ALLOW_HOSTS
class BaseTestCase(StaticLiveServerTestCase):
    """
    Provides base test class which connects to the Docker
    container running Selenium.
    """

    host = "0.0.0.0"  # Bind to 0.0.0.0 to allow external access

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set host to externally accessible web server address
        cls.host = socket.gethostbyname(socket.gethostname())

        # Instantiate the remote WebDriver
        cls.selenium = webdriver.Remote(
            #  Set to: htttp://{selenium-container-name}:port/wd/hub
            #  In our example, the container is named `selenium`
            #  and runs on port 4444
            command_executor="http://selenium:4444/wd/hub",
            # Set to CHROME since we are using the Chrome container
            desired_capabilities=DesiredCapabilities.CHROME,
        )
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


class HomePageTest(BaseTestCase):
    """
    Tests the home page.
    """

    def test_home_page_open(self):
        self.selenium.get(self.live_server_url)
        self.assertIn("SeafloorMappingDB", self.selenium.title)

    def test_home_page_mission_load(self):
        self.selenium.get(self.live_server_url)
        self.assertEquals("5", self.selenium.find_element_by_id("num-missions").text)

    def test_spatial_bounds_link(self):
        self.selenium.find_element_by_id("use_bounds").click()
        self.selenium.find_element_by_id("update-map").click()
        # TODO: test for map bounds in url
        self.assertIn("", self.selenium.current_url)
