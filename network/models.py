from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import os


def user_profile_pic_path(instance, filename):
    """Defines where user profile pictures will be saved"""
    return f'profile_pics/{instance.username}/{filename}'

class User(AbstractUser):
    profile_picture = models.ImageField(
        upload_to=user_profile_pic_path,
        blank=True, 
        null=True, 
    )
    followers = models.ManyToManyField("self", symmetrical=False, related_name="following", blank=True)

    def __str__(self):
        return self.username
    
    @property
    def profile_picture_url(self):
        """Returns the user's profile picture URL or the default image if none is uploaded."""
        if self.profile_picture:
            return self.profile_picture.url
        return os.path.join(settings.STATIC_URL, "network/images/profile_pics/anonymous.jpg")


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)  # Allow empty content (if users uploads pic instead)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def like_count(self):
        return self.likes.count()
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}..."