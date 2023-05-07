from django.urls import path

from blog.views import post_detail, PostListView, post_share, post_comment

app_name = 'blog'

urlpatterns = [
        path('', PostListView.as_view(), name='post_list'),
        path('<int:year>/<int:month>/<int:day>/<slug:post>/',
             post_detail,
             name='post_detail'),
        path('<int:post_id>/share/', post_share, name='post_share'),
        path('<int:post_id>/comment/', post_comment, name='post_comment'),
        ]
