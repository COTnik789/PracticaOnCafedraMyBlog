from django.contrib import admin
from .models import Category, Post, Comment, Profile, Project, Reply, Notification

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'category')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('comment', 'author', 'content', 'created_at')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Notification, NotificationAdmin)