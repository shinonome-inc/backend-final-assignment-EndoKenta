from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from mysite import settings

from .models import Like, Tweet

User = get_user_model()


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.test", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

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
        self.user = User.objects.create_user(
            username="testuser", email="test@test.test", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        tweet = {"content": "tweet"}
        self.client.post(reverse("tweets:create"), tweet)

    def test_success_get(self):
        tweet = Tweet.objects.get(content="tweet")
        response = self.client.get(reverse("tweets:detail", kwargs={"pk": tweet.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet, response.context["tweet"])


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser1", email="test@test.test", password="testpassword"
        )
        self.user = User.objects.create_user(
            username="testuser2", email="test@test.test", password="testpassword"
        )
        self.client.login(username="testuser2", password="testpassword")
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
        self.assertEqual(response.status_code, 404)
        self.assertIn("Not Found", str(response.content))
        self.assertTrue(Tweet.objects.filter(content="tweet").exists())


class TestFavoriteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.test", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        post = {"content": "hello"}
        self.client.post(reverse("tweets:create"), post)
        self.tweet = Tweet.objects.get(content="hello")

    def test_success_post(self):
        response = self.client.post(
            reverse("tweets:like", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(tweet=self.tweet).exists())

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:like", kwargs={"pk": 2}))
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Like.objects.filter(tweet=self.tweet).exists())

    def test_failure_post_with_favorited_tweet(self):
        self.client.post(reverse("tweets:like", kwargs={"pk": self.tweet.pk}))
        response = self.client.post(
            reverse("tweets:like", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.filter(tweet=self.tweet).count(), 1)


class TestUnfavoriteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.test", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        post = {"content": "hello"}
        self.client.post(reverse("tweets:create"), post)
        self.tweet = Tweet.objects.get(content="hello")
        self.client.post(reverse("tweets:like", kwargs={"pk": self.tweet.pk}))

    def test_success_post(self):
        response = self.client.post(
            reverse("tweets:unlike", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(tweet=self.tweet).exists())

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:unlike", kwargs={"pk": 2}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Like.objects.filter(tweet=self.tweet).exists())

    def test_failure_post_with_unfavorited_tweet(self):
        self.client.post(reverse("tweets:unlike", kwargs={"pk": self.tweet.pk}))
        response = self.client.post(
            reverse("tweets:unlike", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
