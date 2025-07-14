from django import forms
from .models import Post, Comment, Category, Reply, Profile
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class PostForm(forms.ModelForm):
    category_name = forms.CharField(
        required=False,
        label='Категория',
        widget=forms.TextInput(attrs={'class': 'form-control', 'list': 'category_suggestions'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_name'].widget.attrs['list'] = 'category_suggestions'

    def save(self, commit=True):
        instance = super().save(commit=False)
        category_name = self.cleaned_data.get('category_name')
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
            instance.category = category
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category_name']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='Ваш комментарий',
        widget=forms.Textarea(attrs={'name': 'content'})  # Изменили с 'comment_content' на 'content'
    )

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(),
        }

class ReplyForm(forms.ModelForm):
    content = forms.CharField(
        label='Ваш ответ',
        widget=forms.Textarea(attrs={'name': 'content'})
    )

    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(),
        }

class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        label='Запомнить меня',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Имя пользователя"
        self.fields['password'].label = "Пароль"

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по заголовку или содержимому'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'website', 'email_notification', 'theme_preference']
        labels = {
            'bio': 'О себе',
            'profile_picture': 'Фотография профиля',
            'website': 'Веб-сайт',
            'email_notification': 'Получать уведомления по email',
            'theme_preference': 'Предпочитаемая тема',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Расскажите о себе (необязательно)'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Ваш веб-сайт (необязательно)'}),
            'email_notification': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'theme_preference': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'email_notification': 'Выберите, если хотите получать уведомления по email.',
        }