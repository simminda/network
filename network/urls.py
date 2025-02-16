
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("create_post/", views.create_post, name="create_post"),
    path("edit/<int:post_id>/", views.edit_post, name="edit_post"),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("follow/<int:user_id>/", views.follow_user, name="follow"),
    path("unfollow/<int:user_id>/", views.unfollow_user, name="unfollow"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("profile/<str:username>/follow/", views.follow_unfollow, name="follow_unfollow"),
    path("following/", views.following_posts, name="following"),
    path("search/", views.search_results, name="search_results"),
]
