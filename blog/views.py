from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.db.models import SlugField

from blog.models import Post


def post_list(request: HttpRequest) -> HttpResponse:
    posts = Post.published.all()
    return render(
            request,
            'blog/post/list.html',
            context={'posts': posts}
            )


def post_detail(request: HttpRequest,
                year: int,
                month: int,
                day: int,
                post: SlugField) -> HttpResponse:

    post = get_object_or_404(
            Post,
            status=Post.Status.PUBLISHED,
            slug=post,
            publish__year=year,
            publish__month=month,
            publish__day=day
           )

    return render(
            request,
            'blog/post/detail.html',
            context={'post': post}
            )
