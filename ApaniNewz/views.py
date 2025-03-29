from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from ApaniNewz.forms import CategoryForm, CommentForm, ContactForm, LJNewsForm, LoginForm, NewsForm, ProfileUpdateForm, RegistrationForm, SubCommentForm, UserUpdate
from .models import Category, Contact, LJNews, Likes, News, Registration, Profile,Comment,SubComments
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

from django.contrib.auth import get_user_model
# Rest Framework API's
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

# Create your views here.

def home(request):  
    
    # Featured News
    featured = News.objects.filter(is_featured=True, status='PUBLISH')
    print(featured)
    # Trending Now
    trending = News.objects.filter(status='PUBLISH').order_by('-created')
    
    categories = Category.objects.filter()
    # Category Wise Show Posts
    cat_news = None
    CATID = request.GET.get('category')
    if CATID:
        cat_news = News.get_all_news_byID(CATID)
    else:
        cat_news = News.objects.filter(is_featured=False,status='PUBLISH').order_by('-created')
    
    # News
    
    news = News.objects.filter(is_featured=False,status='PUBLISH').order_by('-created')
    
    # LJ News
    ljnews = LJNews.objects.filter(status='PUBLISH')
        
    context = {
        'categories':categories,
        'news': news,
        'ljnews':ljnews,
        'trending':trending,
        'featured':featured,
        'cat_news':cat_news
    }
    return render(request, 'Home/index.html',context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'User does not exist')
                return redirect('login')
            if user.check_password(password):
                login(request, user)
                messages.success(request, f"You are now logged in as {email}.")
                return redirect('index')
            else:
                messages.error(request, 'Invalid Password')
                return redirect('login')
        else:
            messages.error(request, 'Invalid Email')
            return redirect('login')
    else:
        form = LoginForm()

    return render(request,"Home/login.html",{'form':form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


def register_view(request):
    if request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()

            role = form.cleaned_data['role']
            enrollment_number = form.cleaned_data.get('enrollment_number') if role == 'Student' else None
            department = form.cleaned_data.get('department')

            # Save profile with or without enrollment_number
            Profile.objects.create(
                user=user,
                department=department,
                enrollment_number=enrollment_number if role == 'Student' else None,  # Only save if Student
                phone=form.cleaned_data['phone'],
                profile_image=form.cleaned_data.get('profile_image')
            )

            messages.success(request, "Your account was successfully created.")
            login(request, user)
            return redirect('index')

    else:
        form = RegistrationForm()

    return render(request, "Home/Registration.html", {'form': form})


@login_required(login_url='login')
def News_Detail(request, id):
    # Recent Post's
    recent = News.objects.filter(status='PUBLISH',is_featured=False).order_by('-created')
    
    
    news = News.objects.filter(id=id)
    ljnews = LJNews.objects.filter(id=id)
    article = get_object_or_404(News, id=id)
    

    # Check if the user liked the article
    like_this_article = Likes.objects.filter(user=request.user, article=article).exists()

    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        comm_id = request.POST.get('comm_id')

        if comm_id:  
            # Save as a SubComment (reply)
            parent_comment = get_object_or_404(Comment, id=int(comm_id))
            SubComments.objects.create(
                news=article,
                user=request.user,
                parent_comment=parent_comment,
                reply=comment_text  # Corrected field
            )
        else:
            # Save as a main Comment
            Comment.objects.create(news=article, user=request.user, comment=comment_text)

    # Fetch comments along with their replies (subcomments)
    comments = [(cm, SubComments.objects.filter(parent_comment=cm)) for cm in Comment.objects.filter(news=article)]

    form = CommentForm()

    # Comment Count
    total_comments = article.total_comments()

    context = {
        'article': article,
        'news': news,
        'like_this_article': like_this_article,
        'comments': comments,
        'form': form,
        "total_comments":total_comments,
        'ljnews':ljnews,
        'recent':recent
    }

    return render(request, "Home/News_Details.html", context)

@login_required(login_url='login')
def like_post(request, id):
    if request.method == "POST":
        article = get_object_or_404(News, id=id)
        Likes.objects.get_or_create(user=request.user, article=article)
        return redirect(request.META.get('HTTP_REFERER') or 'details')
    return redirect('details', id=id)

@login_required(login_url='login')
def unlike_post(request, id):
    if request.method == "POST":
        article = get_object_or_404(News, id=id)
        Likes.objects.filter(user=request.user, article=article).delete()
        return redirect(request.META.get('HTTP_REFERER') or 'details')
    return redirect('details', id=id)

# Search Functionality
@login_required(login_url='login')
def Search_View(request):
    keyword = request.GET.get('keyword')
    articles = News.objects.filter(Q(title__icontains=keyword) | Q(sub_title__icontains=keyword) | Q(content__icontains = keyword),status = "PUBLISH")

    context = {
        'keyword':keyword,
        'articles': articles,
    }
    return render(request, "Home/Search.html",context)

def Contacts(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  # Stay on the same page after submission
        else:
            messages.error(request, "There was an error. Please check your inputs.")
    else:
        form = ContactForm()    
    return render(request, "Home/Contact.html",{'form':form})

def About(request):
    return render(request, "Home/About.html")

def Categories(request):
    categories = Category.objects.filter()
    news = None
    CATID = request.GET.get('category')
    if CATID:
        news = News.get_all_news_byID(CATID)
    else:
        news = News.objects.filter(status='PUBLISH')

    context = {
        'categories': categories,
        'news': news,
    }
    return render(request, "Home/Category.html",context)
    
def LatestNewz(request):
    news = News.objects.filter(status='PUBLISH')
    
    paginator = Paginator(news, 2)  # Show 2 news per page
    page_number = request.GET.get('page')
    NewsDatafinal = paginator.get_page(page_number)
    
    context = {
        'news': news,
        'NewsDatafinal': NewsDatafinal,
        'totalPagelist': range(1, NewsDatafinal.paginator.num_pages + 1),
    }
    
    return render(request, "Home/LatestNewz.html", context)

# Admin Dashbord's
def dashboard(request):
    return render(request,"Admin/Dashboard.html")

def AddNews(request):
    article = News.objects.all()
    categories = Category.objects.all()

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            news = form.save(commit=False)  # ✅ Get model instance but don't save yet
            news.is_featured = request.POST.get('is_featured') == 'on'  # ✅ Handle checkbox manually
            news.save()
            messages.success(request, "News/Article added successfully!")
            return redirect("addnews")
        else:
            messages.error(request, "Form validation failed. Please check your input.")
    else:
        form = NewsForm(user=request.user)

    return render(request, "Admin/AddNews.html", {
        "article": article,
        "categories": categories,
        "form": form,
    })



def AddCategory(request):
    form = CategoryForm()
    categories = Category.objects.filter()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        form.save()
        return redirect("addcategory")
    return render(request,"Admin/AddCategory.html",{'form':form ,'categories':categories})

def Comments(request):
    comments = Comment.objects.all().order_by('-created')  # Latest comments first

    context = {
        'comments': comments,
    }
    return render(request,"Admin/ManageComment.html",context)

def ManageUsers(request):
    user_data = User.objects.all()
    user_profile = Profile.objects.all()
    return render(request,"Admin/ManageUsers.html",{'user_data':user_data,'user_profile':user_profile})

def ManageContact(request):
    return render(request,"Admin/ManageContact.html")

# Account's Details
def ProfilePage(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdate(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile has been updated !')
            return redirect('profile')

    else:
        u_form = UserUpdate(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, "Account/Profile.html",context)

def PostArticle(request):
    cate = Category.objects.all()
    if request.method == 'POST':
        form = LJNewsForm(request.POST, request.FILES)  # ✅ Include request.FILES
        
        if form.is_valid():
            ljnews = form.save(commit=False)  # ✅ Get model instance, but don't save yet
            ljnews.author = f"{request.user.first_name} {request.user.last_name}".strip()  # ✅ Set author field correctly
            ljnews.auther_id = request.user.email  # ✅ Set auther_id field correctly<
            ljnews.save()  # ✅ Now save the instance
            messages.success(request, "News/Article added successfully!")
            return redirect("post_article")
        else:
            messages.error(request, "Form validation failed. Please check your input.")
    else:
        # Prepopulate author field with logged-in user's name
        initial_data = {
            "author": f"{request.user.first_name} {request.user.last_name}".strip()
        }
        form = LJNewsForm(initial=initial_data)
        
    context = {
        "cate": cate,
        "form": form
    }
    return render(request, "Account/PostArticle.html", context)

def Posts(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if not authenticated

    # केवल लॉगिन किए हुए यूज़र की पोस्ट को फ़िल्टर करें
    ljnews = LJNews.objects.filter(author_id=request.user.email, status='PUBLISH')
    
    paginator = Paginator(ljnews, 4)  # Show 2 news per page
    page_number = request.GET.get('page')
    ViewDatafinal = paginator.get_page(page_number)
    
    context = {
        'ViewDatafinal': ViewDatafinal,  # केवल पेजिनेटेड डेटा भेजें
        'totalPage': range(1, ViewDatafinal.paginator.num_pages + 1),
    }
    return render(request, "Account/ViewPosts.html", context)