from django.core.mail import send_mail
from environs import Env

from blog.models import Post

env = Env()
env.read_env()


def send_share_post_email(cleaned_data: dict, url: str, post: Post) -> bool:
    subject = f'{cleaned_data["name"]} recommends you read {post.title}'
    comment = cleaned_data.get('comment')
    message = f'Read {post.title} at {url}\n\n'
    if comment:
        message += f'{cleaned_data["name"]}\'s comments: {comment}'

    sender = env.str('SENDER')
    receiver = cleaned_data['to']
    sent = send_mail(subject, message, sender, [receiver])

    return True if sent == 1 else False
