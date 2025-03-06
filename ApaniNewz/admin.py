from django.contrib import admin

# Register your models here.

from .models import Category, Contact, Likes, News, Profile, Registration,Comment, SubComments

# Register your models here.
@admin.register(Registration)
class UserModelAdmin(admin.ModelAdmin):
    ist_display = ('first_name','last_name','username', 'email','phone', 'profile_image','password','confirm_password','enrollment_number', 'role')


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ('id','category_name')

@admin.register(Likes)
class LikesModelAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created')

# Register your models here.
@admin.register(News)
class NewsModelAdmin(admin.ModelAdmin):
    list_display = ('id','title','sub_title','category','author','content','status','news_image','created','updated')

@admin.register(Profile)
class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ('phone','gender','profile_image','bio', 'location','created','updated')

@admin.register(SubComments)
class SubCommentsModelAdmin(admin.ModelAdmin):
    list_display = ("news", "parent_comment", "user", "reply", "created")

@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = ("news","user","comment","created")

@admin.register(Contact)
class ContectModelAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'email', 'subject','message','created_at')
    search_fields = ('name', 'email', 'subject')