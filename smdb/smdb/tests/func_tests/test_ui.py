from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By


class SeleniumTest(TestCase):
    def setUp(self):
        self.chrome = webdriver.Remote(
            command_executor="http://selenium-hub:4444/wd/hub",
            options=webdriver.ChromeOptions(),
        )
        self.chrome.implicitly_wait(10)
        self.server_url = "http://django:8001"

    def test_visit_site_with_chrome(self):
        self.chrome.get(self.server_url)
        self.assertIn("SeafloorMappingDB", self.chrome.title)
        number = self.chrome.find_element(By.ID, "num-missions").text
        self.assertEqual("5", number)

    # def test_spatial_bounds_link(self):
    #    self.chrome.get(self.server_url)
    #    self.chrome.find_element(By.ID, "use_bounds").click()
    #    self.chrome.find_element(By.ID, "update-map").click()
    #    # TODO: test for map bounds in url
    #    self.assertIn("", self.chrome.current_url)
