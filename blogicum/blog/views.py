from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserChangeForm
from .models import Category, Comment, Post

User = get_user_model()

PAGINATION_LIMIT = 10


def get_filtered_posts():
    return (
        Post.objects.select_related('author', 'location', 'category')
        .filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
        .order_by('-pub_date')
        .annotate(comment_count=Count('comments'))
    )


def index(request):
    paginator = Paginator(get_filtered_posts(), PAGINATION_LIMIT)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        if (not post.is_published
                or not post.category.is_published
                or post.pub_date > timezone.now()):
            raise Http404('Пост не найден')
    comments = post.comments.select_related('author').all()
    form = CommentForm()
    return render(
        request,
        'blog/detail.html',
        {'post': post, 'comments': comments, 'form': form}
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    post_list = get_filtered_posts().filter(category=category)
    paginator = Paginator(post_list, PAGINATION_LIMIT)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = (
        Post.objects.select_related('author', 'location', 'category')
        .filter(author=author)
        .order_by('-pub_date')
        .annotate(comment_count=Count('comments'))
    )
    paginator = Paginator(post_list, PAGINATION_LIMIT)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'blog/profile.html',
        {'profile': author, 'page_obj': page_obj}
    )


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(
        request, 'blog/comment.html', {'form': form, 'comment': comment}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
