from django.contrib import admin

# Register your models here.

from .models import Category, Contact, News, Profile, Registration,Comment

# Register your models here.
@admin.register(Registration)
class UserModelAdmin(admin.ModelAdmin):
    ist_display = ('first_name','last_name','username', 'email','phone', 'profile_image','password','confirm_password')


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ('id','category_name')

# Register your models here.
@admin.register(News)
class NewsModelAdmin(admin.ModelAdmin):
    list_display = ('id','title','sub_title','category','author','content','status','image','created','updated')

@admin.register(Profile)
class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ('phone','gender','profile_image','bio', 'location','created','updated')

@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = ("news","comment","created","updated")

@admin.register(Contact)
class ContectModelAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'email', 'subject','message','created_at')
    search_fields = ('name', 'email', 'subject')