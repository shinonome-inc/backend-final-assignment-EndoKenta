from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserCreationForm


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
