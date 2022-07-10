from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestSignUpView(TestCase):
    def test_success_get(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        DB_num = User.objects.count()
        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/home/")
        self.assertGreater(
            User.objects.count(),
            DB_num,
        )
        self.assertTrue(
            User.objects.filter(username="testuser", email="test@test.test").exists()
        )

    def test_failure_post_with_empty_form(self):
        DB_num = User.objects.count()
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
        self.assertFalse(User.objects.filter(username="", email="").exists())
        self.assertIs(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_empty_username(self):
        DB_num = User.objects.count()
        user = {
            "username": "",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "username", "このフィールドは必須です。")
        self.assertFalse(
            User.objects.filter(username="", email="test@test.test").exists()
        )
        self.assertIs(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_empty_email(self):
        DB_num = User.objects.count()
        user = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)

        self.assertFormError(response, "form", "email", "このフィールドは必須です。")
        self.assertFalse(User.objects.filter(username="testuser", email="").exists())
        self.assertIs(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_empty_password(self):
        DB_num = User.objects.count()
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
        self.assertFalse(
            User.objects.filter(username="testuser", email="test@test.test").exists()
        )
        self.assertIs(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_duplicated_user(self):
        DB_num = User.objects.count()

        self.assertIs(
            User.objects.filter(username="testuser", email="test@test.test").count(), 0
        )
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
        self.assertTrue(
            User.objects.filter(username="testuser", email="test@test.test").exists()
        )
        self.assertIs(
            User.objects.filter(username="testuser", email="test@test.test").count(), 1
        )
        self.assertGreater(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_invalid_email(self):
        DB_num = User.objects.count()

        user = {
            "email": "t@t.t",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "email", "有効なメールアドレスを入力してください。")
        self.assertFalse(
            User.objects.filter(username="testuser", email="t@t.t").exists()
        )
        self.assertIs(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_too_short_password(self):
        DB_num = User.objects.count()

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
        self.assertFalse(
            User.objects.filter(username="testuser", email="test@test.test").exists()
        )
        self.assertIs(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_password_similar_to_username(self):
        DB_num = User.objects.count()

        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)

        self.assertFormError(response, "form", "password2", "このパスワードは ユーザー名 と似すぎています。")
        self.assertFalse(
            User.objects.filter(username="testuser", email="test@test.test").exists()
        )
        self.assertIs(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_only_numbers_password(self):
        DB_num = User.objects.count()

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
        self.assertFalse(
            User.objects.filter(username="testuser", email="test@test.test").exists()
        )
        self.assertIs(
            User.objects.count(),
            DB_num,
        )

    def test_failure_post_with_mismatch_password(self):
        DB_num = User.objects.count()

        user = {
            "username": "testuser",
            "email": "test@test.test",
            "password1": "testpassword",
            "password2": "ttttpppppppp",
        }
        response = self.client.post(reverse("accounts:signup"), user)
        self.assertEqual(response.status_code, 200)

        self.assertFormError(response, "form", "password2", "確認用パスワードが一致しません。")
        self.assertFalse(
            User.objects.filter(username="testuser", email="test@test.test").exists()
        )
        self.assertIs(
            User.objects.count(),
            DB_num,
        )


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
        response = self.client.get(reverse("welcome:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "welcome/home.html")


class TestLoginView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_empty_password(self):
        pass


class TestLogoutView(TestCase):
    def test_success_get(self):
        pass


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
