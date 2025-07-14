from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Post, Category, Comment, Reply, Notification, UserSubscription, CategorySubscription, Profile
from .forms import PostForm, CommentForm, CategoryForm, ReplyForm, LoginForm, RegisterForm, SearchForm, ProfileSettingsForm

def home(request):
    form = SearchForm(request.GET or None)
    posts = Post.objects.all().order_by('-created_at')

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')

        if query:
            posts = posts.filter(title__icontains=query) | posts.filter(content__icontains=query)
        if category:
            posts = posts.filter(category=category)

    theme = 'light'  # Дефолтная тема
    if request.user.is_authenticated:
        try:
            theme = request.user.profile.theme_preference
        except Profile.DoesNotExist:
            Profile.objects.get_or_create(user=request.user, defaults={'bio': '', 'profile_picture': '', 'website': ''})
            theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False) if request.user.is_authenticated else []
    return render(request, 'blog/home.html', {'posts': posts, 'form': form, 'notifications': notifications, 'theme': theme})

def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    comments = post.comment_set.all()
    if request.method == 'POST':
        if 'comment_id' not in request.POST:  # Форма комментария к посту
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.approved = True
                comment.save()
                # Уведомление автору поста о новом комментарии
                if post.author != request.user:
                    Notification.objects.create(
                        user=post.author,
                        message=f'Новый комментарий к вашему посту "{post.title}" от {request.user.username}',
                        notification_type='post_comment',
                        object_id=post.id
                    )
                return redirect('blog:post_detail', pk=pk)
            else:
                messages.error(request, f'Ошибка в форме комментария: {form.errors}')
        else:  # Форма ответа на комментарий
            form = ReplyForm(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.author = request.user
                comment_id = request.POST.get('comment_id')
                if comment_id:
                    try:
                        comment = Comment.objects.get(id=comment_id)
                        reply.comment = comment
                        reply.save()
                        # Уведомление автору комментария о новом ответе
                        if comment.author != request.user:
                            Notification.objects.create(
                                user=comment.author,
                                message=f'Новый ответ на ваш комментарий к посту "{post.title}" от {request.user.username}',
                                notification_type='comment_reply',
                                object_id=comment.id
                            )
                    except Comment.DoesNotExist:
                        messages.error(request, f'Комментарий с ID {comment_id} не найден.')
                    except Exception as e:
                        messages.error(request, f'Ошибка сохранения: {str(e)}')
                else:
                    messages.error(request, 'Отсутствует ID комментария.')
            else:
                messages.error(request, f'Ошибка в форме ответа: {form.errors}')
            return redirect('blog:post_detail', pk=pk)
    comment_form = CommentForm()
    theme = 'light'
    if request.user.is_authenticated:
        try:
            theme = request.user.profile.theme_preference
        except Profile.DoesNotExist:
            Profile.objects.get_or_create(user=request.user, defaults={'bio': '', 'profile_picture': '', 'website': ''})
            theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False) if request.user.is_authenticated else []
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form, 'notifications': notifications, 'theme': theme})

def mark_notification_read(request, notification_id):
    if request.user.is_authenticated:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        # Перенаправление в зависимости от типа уведомления
        if notification.notification_type == 'post_comment':
            return redirect('blog:post_detail', pk=notification.object_id)
        elif notification.notification_type == 'comment_reply':
            comment = get_object_or_404(Comment, id=notification.object_id)
            return redirect('blog:post_detail', pk=comment.post.id)
        elif notification.notification_type == 'new_post':
            return redirect('blog:post_detail', pk=notification.object_id)
    return redirect(request.META.get('HTTP_REFERER', 'blog:home'))

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        request.user.notifications.update(is_read=True)
        return redirect(request.META.get('HTTP_REFERER', 'blog:home'))
    return redirect('blog:home')

def category_list(request):
    categories = Category.objects.all()
    if request.user.is_authenticated:
        subscribed_categories = CategorySubscription.objects.filter(subscriber=request.user).values_list('category_id', flat=True)
    else:
        subscribed_categories = []
    theme = 'light'
    if request.user.is_authenticated:
        try:
            theme = request.user.profile.theme_preference
        except Profile.DoesNotExist:
            Profile.objects.get_or_create(user=request.user, defaults={'bio': '', 'profile_picture': '', 'website': ''})
            theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False) if request.user.is_authenticated else []
    return render(request, 'blog/category_list.html', {'categories': categories, 'subscribed_categories': subscribed_categories, 'notifications': notifications, 'theme': theme})

def category_detail(request, pk):
    category = get_object_or_404(Category, id=pk)
    posts = category.post_set.all()
    theme = 'light'
    if request.user.is_authenticated:
        try:
            theme = request.user.profile.theme_preference
        except Profile.DoesNotExist:
            Profile.objects.get_or_create(user=request.user, defaults={'bio': '', 'profile_picture': '', 'website': ''})
            theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False) if request.user.is_authenticated else []
    return render(request, 'blog/category_detail.html', {'category': category, 'posts': posts, 'notifications': notifications, 'theme': theme})

@login_required
def post_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            category_name = form.cleaned_data.get('category_name')
            if category_name:
                category, created = Category.objects.get_or_create(name=category_name)
                post.category = category
            post.save()
            # Уведомления о новом посте
            for user in User.objects.all():
                if UserSubscription.objects.filter(subscriber=user, author=post.author).exists() or \
                   (post.category and CategorySubscription.objects.filter(subscriber=user, category=post.category).exists()):
                    Notification.objects.create(
                        user=user,
                        message=f'Новый пост "{post.title}" от {post.author.username}',
                        notification_type='new_post',
                        object_id=post.id
                    )
            return redirect('blog:post_detail', pk=post.id)
    else:
        form = PostForm()
    theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'blog/post_create.html', {'form': form, 'categories': categories, 'notifications': notifications, 'theme': theme})

@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, id=pk)
    categories = Category.objects.all()
    if request.user != post.author:
        messages.error(request, 'У вас нет прав для редактирования этого поста.')
        return redirect('blog:post_detail', pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            category_name = form.cleaned_data.get('category_name')
            if category_name:
                category, created = Category.objects.get_or_create(name=category_name)
                post.category = category
            post.save()
            return redirect('blog:post_detail', pk=post.id)
    else:
        form = PostForm(instance=post)
    theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'blog/post_update.html', {'form': form, 'post': post, 'categories': categories, 'notifications': notifications, 'theme': theme})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user != post.author:
        messages.error(request, 'У вас нет прав для удаления этого поста.')
        return redirect('blog:post_detail', pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:home')
    theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'blog/post_delete.html', {'post': post, 'notifications': notifications, 'theme': theme})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Создание профиля для нового пользователя
            Profile.objects.get_or_create(user=user, defaults={'bio': '', 'profile_picture': '', 'website': ''})
            return redirect('blog:home')
        else:
            messages.error(request, 'Ошибка регистрации. Проверь данные.')
    else:
        form = RegisterForm()
    theme = 'light'  # Дефолтная тема для неавторизованных
    notifications = request.user.notifications.filter(is_read=False) if request.user.is_authenticated else []
    return render(request, 'blog/register.html', {'form': form, 'notifications': notifications, 'theme': theme})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if form.cleaned_data['remember_me']:
                request.session.set_expiry(1209600)  # 14 дней
            else:
                request.session.set_expiry(0)  # Сессия до закрытия браузера
            # Проверка и создание профиля, если его нет
            Profile.objects.get_or_create(user=user, defaults={'bio': '', 'profile_picture': '', 'website': ''})
            return redirect('blog:home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    theme = 'light'  # Дефолтная тема для неавторизованных
    notifications = []
    if request.user.is_authenticated:
        try:
            notifications = request.user.notifications.filter(is_read=False)
            theme = request.user.profile.theme_preference
        except Profile.DoesNotExist:
            Profile.objects.get_or_create(user=request.user, defaults={'bio': '', 'profile_picture': '', 'website': ''})
            notifications = request.user.notifications.filter(is_read=False)
            theme = request.user.profile.theme_preference
    return render(request, 'blog/login.html', {'form': form, 'notifications': notifications, 'theme': theme})

def user_logout(request):
    logout(request)
    return redirect('blog:home')

@login_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        Category.objects.create(name=name, description=description)
        return redirect('blog:category_list')
    theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'blog/category_create.html', {'notifications': notifications, 'theme': theme})

@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'blog/my_posts.html', {'posts': posts, 'notifications': notifications, 'theme': theme})

@login_required
def manage_subscriptions(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        target_id = request.POST.get('target_id')
        if action == 'subscribe_author':
            author = get_object_or_404(User, id=target_id)
            UserSubscription.objects.get_or_create(subscriber=request.user, author=author)
            messages.success(request, f'Вы подписались на {author.username}.')
        elif action == 'unsubscribe_author':
            author = get_object_or_404(User, id=target_id)
            UserSubscription.objects.filter(subscriber=request.user, author=author).delete()
            messages.success(request, f'Вы отписались от {author.username}.')
        elif action == 'subscribe_category':
            category = get_object_or_404(Category, id=target_id)
            CategorySubscription.objects.get_or_create(subscriber=request.user, category=category)
            messages.success(request, f'Вы подписались на категорию {category.name}.')
        elif action == 'unsubscribe_category':
            category = get_object_or_404(Category, id=target_id)
            CategorySubscription.objects.filter(subscriber=request.user, category=category).delete()
            messages.success(request, f'Вы отписались от категории {category.name}.')
        return redirect('blog:manage_subscriptions')
    authors = User.objects.exclude(id=request.user.id).distinct()
    categories = Category.objects.all()
    subscribed_authors = UserSubscription.objects.filter(subscriber=request.user).values_list('author_id', flat=True)
    subscribed_categories = CategorySubscription.objects.filter(subscriber=request.user).values_list('category_id', flat=True)
    theme = request.user.profile.theme_preference
    return render(request, 'blog/manage_subscriptions.html', {
        'authors': authors,
        'categories': categories,
        'subscribed_authors': subscribed_authors,
        'subscribed_categories': subscribed_categories,
        'notifications': request.user.notifications.filter(is_read=False),
        'theme': theme
    })

@login_required
def profile_settings(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, bio="", profile_picture="", website="")
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Настройки профиля успешно обновлены.')
            return redirect('blog:profile_settings')
        else:
            messages.error(request, 'Ошибка при обновлении профиля. Проверь данные.')
    else:
        form = ProfileSettingsForm(instance=profile)
    theme = request.user.profile.theme_preference
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'blog/profile_settings.html', {'form': form, 'notifications': notifications, 'theme': theme})