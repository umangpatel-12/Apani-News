from django import forms
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser, Group, Permission


# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Choose Role', 'Choose Role'),
        ('Student', 'Student'),
        ('Faculty/Staff', 'Faculty/Staff'),
    ]
    APPROVED_CHOICES = [
        ('APPROVED', 'APPROVED'),
        ('NOT APPROVED', 'NOT APPROVED'),
    ]

    phone = models.CharField(max_length=10, null=True)
    profile_image = models.ImageField(upload_to='media/profile/', null=True, blank=True)
    approved = models.CharField(max_length=255, choices=APPROVED_CHOICES, null=True, blank=True)
    enrollment_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Choose Role')
    confirm_password = models.CharField(max_length=128)  # This is optional — usually handled in forms, not model

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

    title = models.CharField(max_length=255,unique=True)
    sub_title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    author_id = models.EmailField(max_length=255, editable=False)  # Auto-stored user email
    content = RichTextField(blank=True, null=True)
    status = models.CharField(choices=STATUS,max_length=255)
    is_featured = models.BooleanField(default=False)
    news_image = models.ImageField(upload_to="media/news/")
    likes = models.ManyToManyField(CustomUser, related_name='Post_likes',blank=True)
    views = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """ Automatically save the author's email """
        if not self.pk and hasattr(self, 'author_user'):
            self.author_id = self.author_id.email
        super(News, self).save(*args, **kwargs)
    
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
    
    def total_comments(self):
        comments_count = Comment.objects.filter(news=self).count()
        subcomments_count = SubComments.objects.filter(news=self).count()
        return comments_count + subcomments_count

class LJNews(models.Model):
    STATUS = ('PUBLISH', 'PUBLISH'),('DRAFT', 'DRAFT')
    VISIBILITY_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    title = models.CharField(max_length=255,unique=True)
    sub_title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    author_id = models.EmailField(max_length=255)  # Auto-stored user email
    content = RichTextField(blank=True, null=True)
    status = models.CharField(choices=STATUS, max_length=255)
    visibility = models.CharField(max_length=255, choices=VISIBILITY_CHOICES,null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    likes = models.ManyToManyField(CustomUser, related_name='LjPost_likes',blank=True)
    ljnews_image = models.ImageField(upload_to="media/ljnews/",blank=True, null=True)
    views = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """ Automatically save the author's email """
        if not self.pk and hasattr(self, 'author_user'):
            self.author_id = self.author_id.email
        super(LJNews, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def LJtotal_likes(self):
        count = self.LJNews_likes.count()
        return count

    @staticmethod
    def get_all_ljnews_byID(category_id):
        return LJNews.objects.filter(category=category_id, status='PUBLISH')
    
    def total_comments(self):
        comments_count = Comment.objects.filter(ljnews=self).count()
        subcomments_count = SubComments.objects.filter(ljnews=self).count()
        return comments_count + subcomments_count
 
class Slider(models.Model):
    STATUS = ('PUBLISH', 'PUBLISH'),('DRAFT', 'DRAFT')
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=50)
    content = RichTextField(blank=True, null=True)
    status = models.CharField(choices=STATUS, max_length=255)
    slider_image = models.ImageField(upload_to="media/slider/",blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title 
    
class Gallery(models.Model):
    title = models.CharField(max_length=255)
    gallery_image = models.ImageField(upload_to="media/gallery/")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
       
class Likes(models.Model):
    article = models.ForeignKey(News, on_delete=models.CASCADE, related_name='Post_likes', blank=True, null=True)
    news = models.ForeignKey(LJNews, on_delete=models.CASCADE, related_name='LJNews_likes', blank=True, null=True)    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    # is_liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('article','news', 'user')

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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True)
    enrollment_number = models.CharField(max_length=12, null=True, blank=True,unique=True)  # Add unique enrollment number
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Choose Role')  # Dropdown list
    profile_image = models.ImageField(upload_to='media/profile/')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, blank=True, null=True)
    ljnews = models.ForeignKey(LJNews, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

class SubComments(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, blank=True, null=True)
    ljnews = models.ForeignKey(LJNews, on_delete=models.CASCADE, blank=True, null=True)
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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

class UserOTP(models.Model):
     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
     time_st = models.DateTimeField(default=timezone.now) 
     OTP = models.SmallIntegerField()