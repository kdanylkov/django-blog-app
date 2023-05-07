from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.db.models import SlugField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views.decorators.http import require_POST

from taggit.models import Tag

from blog.models import Post
from blog.forms import EmailPostForm, CommentForm
from blog.services import send_share_post_email


class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request: HttpRequest, tag_slug=None) -> HttpResponse:
    post_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

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
            context={'posts': posts, 'tag': tag}
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
    comments = post.comments.filter(active=True)
    form = CommentForm()

    return render(
            request,
            'blog/post/detail.html',
            context={'post': post, 'comments': comments, 'form': form}
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

    return render(request,
                  'blog/post/share.html',
                  context={'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request,
                  'blog/post/comment.html',
                  context={'post': post, 'form': form, 'comment': comment}
                  )
