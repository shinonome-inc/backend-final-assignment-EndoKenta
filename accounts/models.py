from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.template.defaultfilters import slugify


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(r"^[a-zA-Z0-9]*$", "使用できるのは半角アルファベット、半角数字のみです")],
        help_text="この項目は必須です。半角アルファベット、半角数字で150文字以下にしてください。",
        verbose_name="ユーザー名",
    )
    email = models.EmailField(max_length=254)
    slug = models.SlugField(max_length=150, blank=False, unique=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.username)
        return super().save(*args, **kwargs)


# class FriendShip(models.Model):
#     pass
