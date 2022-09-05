from django.test import TestCase
from django.urls import reverse

from mysite import settings

from .models import Tweet


class TestTweetCreateView(TestCase):
    def setUp(self):
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.client.post(reverse("accounts:signup"), user)

    def test_success_get(self):
        response = self.client.get(reverse("tweets:create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/create.html")

    def test_success_post(self):
        post = {"content": "tweet"}
        response = self.client.post(reverse("tweets:create"), post)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
        self.assertEqual(Tweet.objects.count(), 1)
        self.assertTrue(Tweet.objects.filter(content=post["content"]).exists())

    def test_failure_post_with_empty_content(self):
        post = {"content": ""}
        response = self.client.post(reverse("tweets:create"), post)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "content", "このフィールドは必須です。")
        self.assertEqual(Tweet.objects.count(), 0)

    def test_failure_post_with_too_long_content(self):
        post = {"content": "a" * 141}
        response = self.client.post(reverse("tweets:create"), post)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, "form", "content", "この値は 140 文字以下でなければなりません( 141 文字になっています)。"
        )
        self.assertEqual(Tweet.objects.count(), 0)


class TestTweetDetailView(TestCase):
    def setUp(self):
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.client.post(reverse("accounts:signup"), user)
        tweet = {"content": "tweet"}
        self.client.post(reverse("tweets:create"), tweet)

    def test_success_get(self):
        tweet = Tweet.objects.get(content="tweet")
        response = self.client.get(reverse("tweets:detail", kwargs={"pk": tweet.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet, response.context["tweet"])


class TestTweetDeleteView(TestCase):
    def setUp(self):
        user1 = {
            "username": "testuser1",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        user2 = {
            "username": "testuser2",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.client.post(reverse("accounts:signup"), user1)
        self.client.get(reverse("accounts:logout"))
        self.client.post(reverse("accounts:signup"), user2)
        tweet = {"content": "tweet"}
        self.client.post(reverse("tweets:create"), tweet)

    def test_success_post(self):
        tweet = Tweet.objects.get(content="tweet")
        self.assertEqual(Tweet.objects.count(), 1)
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": tweet.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
        self.assertEqual(Tweet.objects.count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": 2}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Tweet.objects.filter(content="tweet").exists())

    def test_failure_post_with_incorrect_user(self):
        self.client.get(reverse("accounts:logout"))
        self.client.login(username="testuser1", password="testpassword")
        tweet = Tweet.objects.get(content="tweet")
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": tweet.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertIn("403 Forbidden", str(response.content))
        self.assertTrue(Tweet.objects.filter(content="tweet").exists())


class TestFavoriteView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_favorited_tweet(self):
        pass


class TestUnfavoriteView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_unfavorited_tweet(self):
        pass
