import random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from ApaniNews import settings
from ApaniNewz.forms import CategoryForm, CommentForm, ContactForm, LJNewsForm, LoginForm, NewsForm, ProfileUpdateForm, RegistrationForm, SubCommentForm, UserUpdate
from .models import Category, Contact, LJNews, Likes, News, Registration, Profile,Comment,SubComments, UserOTP
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Count
from django.core.mail import send_mail
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
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Static admin login
            if email == 'admin@gmail.com' and password == 'admin@123':
                try:
                    admin_user = User.objects.get(email=email)
                except User.DoesNotExist:
                    # Create admin user if it doesn't exist
                    admin_user = User.objects.create_user(
                        username='admin',
                        email=email,
                        password=password
                    )
                    admin_user.is_staff = True
                    admin_user.is_superuser = True
                    admin_user.save()

                login(request, admin_user)
                messages.info(request, "You are now logged in as admin.")
                return redirect('dashboard')  # Redirect to admin dashboard

            # Regular user login flow
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'This email is not registered.')
                return render(request, 'Home/login.html', {'form': form})

            if not user.is_active:
                messages.error(request, "Your account isn't active.")
                return render(request, 'Home/login.html', {'form': form})

            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {email}.")
                request.session['user_id'] = user.id
                request.session['email'] = email
                return redirect('index')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()

    return render(request, 'Home/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

# def register_view(request):
#     if request.user.is_authenticated:
#         return redirect('login')

#     if request.method == 'POST':
#         get_OTP = request.POST.get('OTP')
#         form = RegistrationForm(request.POST, request.FILES)
        
#         if get_OTP:
#             get_user = request.POST.get('user')
#             user = User.objects.get(email=get_user)
            
#             if int(get_OTP) == UserOTP.objects.filter(user=user).last().OTP:
#                 user.is_active = True
#                 login(request, user)
#                 user.save()
#                 messages.success(request, "Your account was successfully created.")
#                 return render(request, 'Home/login.html', {'form': form})
#             else:
#                 messages.error(request, "You entered a wrong OTP.")
#                 return render(request, "Home/Registration.html", {'OTP': True, 'user': user})
        
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.is_active = False
#             user.save()
#             otp_code = random.randint(100000, 999999)
#             UserOTP.objects.create(user=user, OTP=otp_code)

#             # Format professional OTP email
#             subject = "Verify Your Email Address - OTP Code"
#             message = f"""
#                         Hi {user.first_name},

#                         Thank you for registering with us!

#                         Please use the One-Time Password (OTP) below to verify your email address and activate your account:

#                         🔐 OTP Code: {otp_code}

#                         This OTP is valid for a limited time and should not be shared with anyone.

#                         If you did not attempt to register, please ignore this email.

#                         Regards,  
#                         Team Support  
#                         """

#             send_mail(
#                 subject,
#                 message.strip(),
#                 settings.EMAIL_HOST_USER,
#                 [user.email],
#                 fail_silently=False,
#             )

#             role = form.cleaned_data['role']
#             enrollment_number = form.cleaned_data.get('enrollment_number') if role == 'Student' else None
#             department = form.cleaned_data.get('department')

#             # Save profile with or without enrollment_number
#             Profile.objects.create(
#                 user=user,
#                 department=department,
#                 enrollment_number=enrollment_number if role == 'Student' else None,  # Only save if Student
#                 phone=form.cleaned_data['phone'],
#                 profile_image=form.cleaned_data.get('profile_image')
#             )
#             messages.info(request, "We’ve sent you an OTP to your email. Please enter it below to verify your account.")
#             messages.success(request, "Your account was successfully created.")
#             login(request, user)
#             return redirect('index')

#     else:
#         form = RegistrationForm()

#     return render(request, "Home/Registration.html", {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')  # Redirect authenticated users to index

    if request.method == 'POST':
        otp_input = request.POST.get('OTP')
        form = RegistrationForm(request.POST, request.FILES)

        # OTP Verification Block
        if otp_input:
            email = request.POST.get('user')
            try:
                user = User.objects.get(email=email)
                user_otp = UserOTP.objects.filter(user=user).last()
                
                if user_otp and int(otp_input) == user_otp.OTP:
                    user.is_active = True
                    user.save()
                    login(request, user)
                    messages.success(request, "Your account has been successfully verified and logged in.")
                    return redirect('index')
                else:
                    messages.error(request, "Invalid OTP. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "No user found for verification.")

            return render(request, "Home/Registration.html", {'OTP': True, 'user': email})

        # Registration Form Handling
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()

            otp_code = random.randint(100000, 999999)
            UserOTP.objects.create(user=user, OTP=otp_code)

            # Format professional OTP email
            subject = "Verify Your Email Address - OTP Code"
            message = f"""
                        Hi {user.first_name},

                        Thank you for registering with us!

                        Please use the One-Time Password (OTP) below to verify your email address and activate your account:

                        🔐 OTP Code: {otp_code}

                        This OTP is valid for a limited time and should not be shared with anyone.

                        If you did not attempt to register, please ignore this email.

                        Regards,  
                        Team Support  
                        """

            send_mail(
                subject,
                message.strip(),
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently = False,
            )

            role = form.cleaned_data['role']
            department = form.cleaned_data.get('department')
            enrollment_number = form.cleaned_data.get('enrollment_number') if role == 'Student' else None
            Profile.objects.create(
                user=user,
                department=department,
                enrollment_number=enrollment_number if role == 'Student' else None,  # Only save if Student
                phone=form.cleaned_data['phone'],
                profile_image=form.cleaned_data.get('profile_image')
            )

            messages.info(request, "We’ve sent you an OTP to your email. Please enter it below to verify your account.")
            return render(request, "Home/Registration.html", {'OTP': True, 'user': user.email})

        else:
            messages.error(request, "Please correct the errors in the form.")

    else:
        form = RegistrationForm()

    return render(request, "Home/Registration.html", {'form': form})

def ResendOTP(request):
    if request.method == 'GET':
        get_user = request.GET['user']
        if User.objects.filter(email = get_user).exists() and not User.objects.get(email = get_user).is_active:
            user = User.objects.get(email= get_user)
            user_OTP = random.randint(100000, 999999)
            UserOTP.objects.create(user=user, OTP=user_OTP)
            subject = 'Your OTP Verification Code'
             # Format professional OTP email
            subject = "Verify Your Email Address - OTP Code"
            message = f"""
                        Hi {user.first_name}{user.last_name},

                        Thank you for registering with us!

                        Please use the One-Time Password (OTP) below to verify your email address and activate your account:

                        🔐 OTP Code: {user_OTP}

                        This OTP is valid for a limited time and should not be shared with anyone.

                        If you did not attempt to register, please ignore this email.

                        Regards,  
                        Team Support  
                        """
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently = False
            )
            return HttpResponse("Re-Send")
    return HttpResponse("Can't send")

@login_required(login_url='login')
def News_Detail(request, id):
    # Category Wise Show Posts
    category = Category.objects.annotate(post_count=Count('news'))
    
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
        'recent':recent,
        'category':category
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

# Category search on details page
def CategorySearch(request,id):
    category = get_object_or_404(Category, id=id)
    posts = News.objects.filter(category=category)
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, "Home/CategorySearch.html", context)

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
    
    recent = News.objects.filter(status='PUBLISH',is_featured=False).order_by('-created')
    
    paginator = Paginator(news, 2)  # Show 2 news per page
    page_number = request.GET.get('page')
    NewsDatafinal = paginator.get_page(page_number)
    
    context = {
        'news': news,
        'NewsDatafinal': NewsDatafinal,
        'totalPagelist': range(1, NewsDatafinal.paginator.num_pages + 1),
        'recent':recent,
    }
    
    return render(request, "Home/LatestNewz.html", context)

# Admin Dashbord's
def dashboard(request):
    return render(request,"Admin/Dashboard.html")

def AddNews(request):
    article = News.objects.all()
    categories = Category.objects.all()

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)

        if form.is_valid():
            news = form.save(commit=False)  # ✅ Get model instance but don't save yet
            news.is_featured = request.POST.get('is_featured') == 'on'  # ✅ Handle checkbox manually
            news.save()
            messages.success(request, "News/Article added successfully!")
            return redirect("addnews")
        else:
            messages.error(request, "Form validation failed. Please check your input.")
    else:
        form = NewsForm()


    paginator = Paginator(article, 5)  # Show 5 articles per page
    page_number = request.GET.get('page')  # Get page number from URL
    page_obj = paginator.get_page(page_number)  # Get the current page

    total_pages = range(1, paginator.num_pages + 1)  # List of all pages
    
    return render(request, "Admin/AddNews.html", {
        "article": article,
        "categories": categories,
        "form": form,
        "NewsData": page_obj,  # Pagination info
        "totalPagelist": total_pages,
    })

# def EDITNews(request, id):
#     news = get_object_or_404(News, id=id)
#     categories = Category.objects.all()

#     if request.method == 'POST':
#         title = request.POST.get('title')
#         sub_title = request.POST.get('sub_title')
#         category_id = request.POST.get('category')
#         author = request.POST.get('author')
#         content = request.POST.get('content')
#         status = request.POST.get('status')
#         is_featured = request.POST.get('is_featured') == 'on'  # Checkbox handling

#         # Get the category instance
#         category = get_object_or_404(Category, id=category_id)

#         # Assign values to news object
#         news.title = title
#         news.sub_title = sub_title
#         news.category = category
#         news.author = author
#         news.content = content
#         news.status = status
#         news.is_featured = is_featured

#         # Image upload check
#         if 'news_image' in request.FILES:
#             news.news_image = request.FILES['news_image']

#         # Save updated news
#         news.save()
#         messages.success(request, "News updated successfully!")
#         return redirect('addnews')

#     context = {
#         'news': news,
#         'categories': categories
#     }
#     return render(request, 'Admin/AddNews.html', context)

def EDITNews(request, id):
    news = get_object_or_404(News, id=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "News updated successfully!")
            return redirect('addnews')
    else:
        form = NewsForm(instance=news)

    return render(request, 'Admin/AddNews.html', {
        'form': form,
        'news': news,
        'categories': categories
    })

def deletenews(request, id):
    news = News.objects.filter(id=id)
    news.delete()
    messages.success(request, "News/Article deleted successfully!")
    return redirect("addnews")

def AddCategory(request):
    form = CategoryForm()
    categories = Category.objects.filter()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        form.save()
        return redirect("addcategory")
    return render(request,"Admin/AddCategory.html",{'form':form ,'categories':categories})

def EditCategory(request, id):
    categories = get_object_or_404(Category, pk=id)
    if request.method == 'POST':
        new_name = request.POST.get('category_name')
        if new_name:
            categories.category_name = new_name
            categories.save()
            messages.success(request, 'Category updated successfully.')
        else:
            messages.warning(request, 'Category name cannot be empty.')
        return redirect('addcategory')
    return render(request, "Admin/AddCategory.html", {'categories':categories})

def DeleteCategory(request, id):
    categories = get_object_or_404(Category, pk=id)
    if request.method == 'POST':
        categories.delete()
        messages.success(request, 'Category deleted successfully.')
    return redirect("addcategory")

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
    contact = Contact.objects.all()
    context = {
        'contact':contact
    }
    return render(request,"Admin/ManageContact.html",context)

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