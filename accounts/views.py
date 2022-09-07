from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

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
        return context
