from django.contrib import admin
from .models import (
    Registration, Category, News, LJNews, Likes, 
    Profile, Comment, SubComments, Contact, UserOTP
)

# Register Registration model (custom user)
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'department')
    search_fields = ('email', 'username', 'role', 'department')

# Register Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender', 'role', 'enrollment_number')
    search_fields = ('user__username', 'phone', 'role')

# Register Category
admin.site.register(Category)

# Register News
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created')
    list_filter = ('status', 'category')
    search_fields = ('title', 'author')

# Register LJNews
@admin.register(LJNews)
class LJNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status','visibility','created')
    list_filter = ('status', 'category')
    search_fields = ('title', 'author')
    
    def approve_news(self, request, queryset):
        queryset.update(status='approved')
    approve_news.short_description = "Approve selected News"

# Register Likes
@admin.register(Likes)
class LikesAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created')

# Register Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('news', 'user', 'comment', 'created')

# Register SubComments
@admin.register(SubComments)
class SubCommentsAdmin(admin.ModelAdmin):
    list_display = ('news', 'parent_comment', 'user', 'reply', 'created')

# Register Contact
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')

# Register UserOTP
@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'OTP', 'time_st')
