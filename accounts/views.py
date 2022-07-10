from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from .forms import UserCreationForm


class WelcomeView(TemplateView):
    template_name = "welcome/index.html"


class SignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("welcome:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, email=email, password=password)
        login(self.request, user)
        return response
