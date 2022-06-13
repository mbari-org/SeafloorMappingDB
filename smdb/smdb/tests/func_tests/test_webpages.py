import pytest
from django.test import TestCase
from django.urls import reverse
from selenium import webdriver

pytestmark = pytest.mark.django_db


class FunctionalTestCase(TestCase):
    LOGIN_URL = "http://localhost:8000/login/"
    ADMIN_URL = "http://localhost:8000/admin/login/?next=/admin/"

    @pytest.fixture(autouse=True)
    def setup(self):
        self.browser = webdriver.Chrome()
        yield
        self.tearDown()

    @pytest.mark.django_db
    def test_there_is_homepage(self):
        self.browser.get("http://localhost:8000")
        self.assertIn("Blog", self.browser.page_source)
        # assert True == True

    @pytest.mark.django_db
    def test_actions_dropdown_button_works(self):
        self.browser.get("http://localhost:8000")
        self.browser.find_element_by_class_name("dropdown-toggle").click()
        # FIND WAY TO CHECK IF 'All Articles' <a/> IS VISIBLE
        self.assertIn("All Articles", self.browser.page_source)
        all_articles_btn = self.browser.find_element_by_xpath(
            "//a[contains(text(), 'All Articles')]"
        )
        if all_articles_btn.is_displayed():
            assert True
        else:
            pytest.fail()
