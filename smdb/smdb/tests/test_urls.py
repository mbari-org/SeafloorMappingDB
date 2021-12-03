from django.urls import reverse, resolve


class TestUrls:
    def test_post_content_url(self):
        path = reverse("home")
        assert resolve(path).view_name == "home"
        path = reverse("about")
        assert resolve(path).view_name == "about"
