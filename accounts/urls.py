from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path(
        "login/", LoginView.as_view(template_name="accounts/login.html"), name="login"
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path('home/', views.HomeView.as_view(), name='home'),
    # path('', include('django.contrib.auth.urls')),
    path(
        "profile/<slug:slugified_username>",
        views.UserProfileView.as_view(),
        name="user_profile",
    ),
    # path('profile/edit/', views.UserProfileEditView.as_view(), name='user_profile_edit'),
    path(
        "<str:username>/following_list/",
        views.FollowingListView.as_view(),
        name="following_list",
    ),
    path(
        "<str:username>/follower_list/",
        views.FollowerListView.as_view(),
        name="follower_list",
    ),
    path("<str:username>/follow/", views.follow_view, name="follow"),
    path("<str:username>/unfollow/", views.unfollow_view, name="unfollow"),
]
