from django.contrib import admin
from apps.community.models import Post, Comment, Event, EventRSVP


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'post_type', 'author', 'company', 'is_pinned', 'visibility', 'created_at']
    list_filter = ['post_type', 'visibility', 'is_pinned']
    search_fields = ['title', 'content']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'is_deleted', 'created_at']
    list_filter = ['is_deleted']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'start_datetime', 'location', 'is_public']
    list_filter = ['is_public']
    search_fields = ['title']


@admin.register(EventRSVP)
class EventRSVPAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'status', 'updated_at']
    list_filter = ['status']
