"""Pytest fixtures for Selenium / live-server functional tests."""
import os
import socket

import pytest
from selenium import webdriver


@pytest.fixture
def chrome():
    """Remote Chrome WebDriver for use in Docker (selenium-hub)."""
    options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
        command_executor=os.environ.get(
            "SELENIUM_HUB_URL",
            "http://selenium-hub:4444/wd/hub",
        ),
        options=options,
    )
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture
def live_server_url_for_selenium(live_server):
    """URL for the live server reachable from the Selenium browser (e.g. Chrome in Docker)."""
    # In Docker, use hostname so Chrome container can resolve this container on the same network
    host = os.environ.get(
        "SELENIUM_LIVE_SERVER_HOST",
        socket.gethostname() or "localhost",
    )
    # So Django accepts the Host header when the browser connects via this hostname
    from django.conf import settings

    if host not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]
    port = live_server.thread.port
    return f"http://{host}:{port}"
