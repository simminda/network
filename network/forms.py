from django import forms
from .models import Post, User


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Write something...",
            "rows": 3
        }),
        label=""
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Post
        fields = ["content", "image"]


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "profile_picture"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "profile_picture": forms.FileInput(attrs={"class": "form-control"}),
        }