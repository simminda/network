from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db import models


from .models import User
from .models import Post
from .forms import PostForm, EditProfileForm


def index(request):
    posts_list = Post.objects.all().order_by("-timestamp")  # Newest posts first
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page

    page_number = request.GET.get("page")  
    posts = paginator.get_page(page_number)  

    return render(request, "network/index.html", {
        "posts": posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("index")  # Redirect to homepage after posting
    else:
        form = PostForm()
    
    return render(request, "network/create_post.html", {"form": form})


@csrf_exempt
@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        post = Post.objects.get(id=post_id, user=request.user)
        new_content = data.get("content", "").strip()

        if not new_content and not post.image:
            return JsonResponse({"error": "Post must have text or an image."}, status=400)

        post.content = new_content
        post.save()

        return JsonResponse({"message": "Post updated successfully", "content": post.content}, status=200)
    
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found or permission denied"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)  # Unlike
        liked = False
    else:
        post.likes.add(request.user)  # Like
        liked = True

    return JsonResponse({"liked": liked, "like_count": post.like_count()})


@login_required
def follow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.user != target_user:
        request.user.following.add(target_user)
    return redirect("profile", user_id=user_id)

@login_required
def unfollow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.user != target_user:
        request.user.following.remove(target_user)
    return redirect("profile", user_id=user_id)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    is_following = request.user.is_authenticated and request.user in user.followers.all()
    
    return render(request, "network/profile.html", {
        "profile_user": user,
        "posts": page_obj,
        "followers_count": user.followers.count(),
        "following_count": user.following.count(),
        "is_following": is_following
    })

@login_required
def follow_unfollow(request, username):
    user_to_toggle = get_object_or_404(User, username=username)

    if request.user == user_to_toggle:
        return JsonResponse({"error": "You cannot follow yourself"}, status=400)

    if request.user in user_to_toggle.followers.all():
        user_to_toggle.followers.remove(request.user)
        is_following = False
    else:
        user_to_toggle.followers.add(request.user)
        is_following = True

    return JsonResponse({"is_following": is_following, "followers_count": user_to_toggle.followers.count()})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile", username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "network/edit_profile.html", {"form": form})


@login_required
def following_posts(request):
    following_users = request.user.following.all()
    posts = Post.objects.filter(user__in=following_users).order_by("-timestamp").annotate(like_count=models.Count("likes"))

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {"posts": page_obj})


def search_results(request):
    query = request.GET.get("q", "").strip()
    users = []
    posts = []
    
    if query:
        users = User.objects.filter(username__icontains=query)
        posts = Post.objects.filter(content__icontains=query).order_by("-timestamp")

    return render(request, "network/search.html", {
        "query": query,
        "users": users,
        "posts": posts
    })