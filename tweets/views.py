from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    context_object_name = "tweets"
    queryset = (
        Tweet.objects.select_related("user")
        .prefetch_related("like_set")
        .order_by("-created_at")
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["liked_list"] = Like.objects.filter(user=self.request.user).values_list(
            "tweet", flat=True
        )
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    fields = ["content"]
    template_name = "tweets/create.html"
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/detail.html"


class TweetDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "tweets/delete.html"
    model = Tweet
    success_url = reverse_lazy("tweets:home")

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(user=self.request.user)


@login_required
@require_POST
def like_view(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    Like.objects.get_or_create(tweet=tweet, user=request.user)
    liked = True

    context = {
        "tweet_id": tweet.id,
        "liked": liked,
        "count": tweet.like_set.count(),
    }

    return JsonResponse(context)


@login_required
@require_POST
def unlike_view(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if like := Like.objects.filter(tweet=tweet, user=request.user).select_related(
        "tweet", "user"
    ):
        like.delete()
    liked = False

    context = {
        "tweet_id": tweet.id,
        "liked": liked,
        "count": tweet.like_set.count(),
    }

    return JsonResponse(context)
