from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

from .models import Comment, Post

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'location',
            'category',
            'image',
        )


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )
