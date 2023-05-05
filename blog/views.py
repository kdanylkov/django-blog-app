from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.db.models import SlugField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

from blog.models import Post
from blog.forms import EmailPostForm
from blog.services import send_share_post_email


class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request: HttpRequest) -> HttpResponse:
    post_list = Post.published.all()

    # Pagination with for 3 blog posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # Exception handling for cases when the returned page does not exist
        # If the page_number is out of range we deliver
        # the last page of the results.
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # If page number value is not an integer, the returned page_number
        # is the first page by default
        posts = paginator.page(1)

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


def post_share(request: HttpRequest, post_id: int) -> HttpResponse:

    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                    post.get_absolute_url()
                    )
            sent = send_share_post_email(cd, post_url, post)
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})
