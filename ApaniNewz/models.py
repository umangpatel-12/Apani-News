from django import forms
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



# Custom User Model

# Create your models here.
class Registration(AbstractUser):

    ROLE_CHOICES = [
        ('Choose Role', 'Choose Role'),
        ('Student', 'Student'),
        ('Faculty/Staff', 'Faculty/Staff'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, null=True)
    profile_image = models.ImageField(upload_to='media/profile/')
    enrollment_number = models.CharField(max_length=12, unique=True,null=True, blank=True)  # Add unique enrollment number
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Choose Role')  # Dropdown list
    password = models.CharField(max_length=128)
    confirm_password = models.CharField(max_length=128)

    groups = models.ManyToManyField(Group, related_name='registration_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='registration_user_permissions', blank=True)

    def __str__(self):
        return self.email
    
#Category
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    
    def __str__(self):
            return self.category_name
    
class News(models.Model):
    STATUS = ('PUBLISH','PUBLISH'),('DRAFT','DRAFT')

    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    content = RichTextField(blank=True, null=True)
    status = models.CharField(choices=STATUS,max_length=255)
    news_image = models.ImageField(upload_to="media/news/")
    likes = models.ManyToManyField(User, related_name='Post_likes',blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @staticmethod
    def get_all_news_byID(category_id):
         if category_id:
            return News.objects.filter(category = category_id)
         else:
              return News.objects.all()
         
    def total_likes(self):
        count = self.Post_likes.count()
        return count
         
class Likes(models.Model):
    article = models.ForeignKey(News, on_delete=models.CASCADE, related_name='Post_likes')    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    # is_liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('article', 'user')


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    ROLE_CHOICES = [
        ('Choose Role', 'Choose Role'),
        ('Student', 'Student'),
        ('Faculty/Staff', 'Faculty/Staff'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    enrollment_number = models.CharField(max_length=12, null=True, blank=True,unique=True)  # Add unique enrollment number
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Choose Role')  # Dropdown list
    profile_image = models.ImageField(upload_to='media/profile/')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

class SubComments(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reply

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
