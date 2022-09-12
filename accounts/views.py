from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from accounts.models import FriendShip
from tweets.models import Tweet

from .forms import SignUpForm

User = get_user_model()


class SignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, email=email, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile"
    slug_field = "slugified_username"
    slug_url_kwarg = "slugified_username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweets"] = Tweet.objects.filter(user=self.get_object().pk).order_by(
            "-created_at"
        )
        context["profile_username"] = self.get_object().username
        context["follow_count"] = FriendShip.objects.filter(
            follow__username=self.kwargs["slugified_username"]
        ).count()
        context["follower_count"] = FriendShip.objects.filter(
            followed__username=self.kwargs["slugified_username"]
        ).count()
        if self.request.user.username is not self.kwargs["slugified_username"]:
            result = FriendShip.objects.filter(
                follow__username=self.request.user.username
            ).filter(followed__username=self.kwargs["slugified_username"])
            context["connected"] = True if result else False

        return context


@login_required
def follow_view(request, *args, **kwargs):
    try:
        follow = User.objects.get(username=request.user.username)
        followed = User.objects.get(username=kwargs["username"])
    except User.DoesNotExist:
        messages.warning(request, "{}は存在しません".format(kwargs["username"]))
        raise Http404()
    if follow == followed:
        messages.warning(request, "自分自身はフォローできません")
    else:
        _, created = FriendShip.objects.get_or_create(follow=follow, followed=followed)

        if created:
            messages.success(request, "{}をフォローしました".format(followed.username))
        else:
            messages.warning(request, "あなたはすでに{}をフォローしています".format(followed.username))

    return HttpResponseRedirect(
        reverse_lazy(
            "accounts:user_profile", kwargs={"slugified_username": kwargs["username"]}
        )
    )


@login_required
def unfollow_view(request, *args, **kwargs):
    try:
        follow = User.objects.get(username=request.user.username)
        followed = User.objects.get(username=kwargs["username"])
        if follow == followed:
            messages.warning(request, "自分自身のフォローは外せません")
        else:
            unfollow = FriendShip.objects.get(follow=follow, followed=followed)
            unfollow.delete()
            messages.success(request, "あなたは{}のフォローを外しました".format(followed.username))
    except User.DoesNotExist:
        messages.warning(request, "{}は存在しません".format(kwargs["username"]))
        raise Http404("{}は存在しません".format(kwargs["username"]))
    except FriendShip.DoesNotExist:
        messages.warning(request, "あなたは{}をフォローしていません".format(followed.username))
        raise Http404()
    return HttpResponseRedirect(
        reverse_lazy(
            "accounts:user_profile", kwargs={"slugified_username": kwargs["username"]}
        )
    )


class FollowingListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/following_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = kwargs["username"]
        context["followings"] = FriendShip.objects.select_related(
            "follow", "followed"
        ).filter(follow__username=self.kwargs["username"])
        context["follow_count"] = FriendShip.objects.filter(
            follow__username=self.kwargs["username"]
        ).count()
        return context


class FollowerListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/follower_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = kwargs["username"]
        context["followers"] = FriendShip.objects.select_related(
            "follow", "followed"
        ).filter(followed__username=self.kwargs["username"])
        context["followed_count"] = FriendShip.objects.filter(
            followed__username=self.kwargs["username"]
        ).count()
        return context
