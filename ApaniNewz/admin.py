from django.contrib import admin
from .models import (
    CustomUser, Gallery, Category, News, LJNews, Likes, 
    Profile, Comment, Slider, SubComments, Contact, UserOTP
)
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register Registration model (custom user)
# @admin.register(Registration)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            'fields': ('phone', 'profile_image', 'approved', 'enrollment_number', 'department', 'role')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

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

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'author','content','slider_image','status', 'created')
    
@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'gallery_image', 'created')
    search_fields = ('title',)

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
