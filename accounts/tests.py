from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from mysite import settings

User = get_user_model()


class TestSignUpView(TestCase):
    def test_success_get(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(
            User.objects.filter(username="testuser", email="test@test.test").exists()
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        user = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "email", "このフィールドは必須です。")
        self.assertFormError(response, "form", "username", "このフィールドは必須です。")
        self.assertFormError(response, "form", "password1", "このフィールドは必須です。")
        self.assertFormError(response, "form", "password2", "このフィールドは必須です。")
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_empty_username(self):
        user = {
            "username": "",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "username", "このフィールドは必須です。")
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_empty_email(self):
        user = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "email", "このフィールドは必須です。")
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_empty_password(self):
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "password1", "このフィールドは必須です。")
        self.assertFormError(response, "form", "password2", "このフィールドは必須です。")
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_duplicated_user(self):
        user1 = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        user2 = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.client.post(reverse("accounts:signup"), user1)
        response = self.client.post(reverse("accounts:signup"), user2)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "username", "同じユーザー名が既に登録済みです。")
        self.assertEqual(
            User.objects.filter(username="testuser", email="test@test.test").count(), 1
        )

    def test_failure_post_with_invalid_email(self):
        user = {
            "email": "t@t.t",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "email", "有効なメールアドレスを入力してください。")
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_too_short_password(self):
        user = {
            "email": "test@test.test",
            "username": "testuser",
            "password1": "pass",
            "password2": "pass",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, "form", "password2", "このパスワードは短すぎます。最低 8 文字以上必要です。"
        )
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_password_similar_to_username(self):
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)

        self.assertFormError(response, "form", "password2", "このパスワードは ユーザー名 と似すぎています。")
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_only_numbers_password(self):
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "1234567890",
            "password2": "1234567890",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)

        self.assertFormError(
            response, "form", "password2", "このパスワードは一般的すぎます。", "このパスワードは数字しか使われていません。"
        )
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_mismatch_password(self):
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "ttttpppppppp",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)

        self.assertFormError(response, "form", "password2", "確認用パスワードが一致しません。")
        self.assertEqual(User.objects.count(), 0)


class TestHomeView(TestCase):
    def setUp(self):
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.client.post(reverse("accounts:signup"), user)

    def test_success_get(self):
        response = self.client.get(reverse("tweets:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.test", password="testpassword"
        )

    def test_success_get(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        user = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(reverse("accounts:login"), user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        user = {
            "username": "aaaaaaaa",
            "password": "testpassword",
        }
        response = self.client.post(reverse("accounts:login"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, "form", "", "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。"
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        user = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(reverse("accounts:login"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "password", "このフィールドは必須です。")
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.test", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def test_success_get(self):
        pass


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_user(self):
        pass

    def test_failure_post_with_self(self):
        pass


class TestUnfollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowingListView(TestCase):
    def test_success_get(self):
        pass


class TestFollowerListView(TestCase):
    def test_success_get(self):
        pass
