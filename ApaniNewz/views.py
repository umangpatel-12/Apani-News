import json
import random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from ApaniNews import settings
from ApaniNewz.forms import CategoryForm, CommentForm, ContactForm, LJNewsForm, LoginForm, NewsForm, ProfileUpdateForm, RegistrationForm, SliderForm, SubCommentForm, UserUpdate
from .models import Category, Contact, CustomUser, LJNews, Likes, News, Profile,Comment, Slider,SubComments, UserOTP
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
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils.timezone import now, timedelta
from collections import defaultdict
# Create your views here.


@login_required(login_url='login')
def home(request):  
    
    # Slider
    # slider = LJNews.objects.filter(status='PUBLISH', visibility='APPROVED')
    slider = Slider.objects.filter(status='PUBLISH').order_by('-created')  # Get the latest 5 sliders
    
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
    ljnews = None
    catid = request.GET.get('category')
    if catid:
        ljnews = LJNews.get_all_ljnews_byID(catid)
    else:
        ljnews = LJNews.objects.filter(status='PUBLISH',visibility='APPROVED').order_by('-created')
    
        
    context = {
        'categories':categories,
        'news': news,
        'ljnews':ljnews,
        'trending':trending,
        'featured':featured,
        'cat_news':cat_news,
        'slider':slider
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
                    admin_user = CustomUser.objects.get(email=email)
                except CustomUser.DoesNotExist:
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
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
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
                print(form.errors)
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
                user = CustomUser.objects.get(email=email)
                user_otp = UserOTP.objects.filter(user=user).last()
                
                if user_otp and int(otp_input) == user_otp.OTP:
                    user.is_active = True
                    user.approved = 'NOT APPROVED'  # Ensure user is 'NOT APPROVED' until verified
                    user.save()
                    login(request, user)
                    messages.success(request, "Your account has been successfully verified and logged in.")
                    return redirect('login')
                else:
                    messages.error(request, "Invalid OTP. Please try again.")
            except CustomUser.DoesNotExist:
                messages.error(request, "No user found for verification.")

            return render(request, "Home/Registration.html", {'OTP': True, 'user': email})

        # Registration Form Handling
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Account not active until OTP verification
            user.approved = 'NOT APPROVED'  # Default to 'NOT APPROVED'
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
                fail_silently=False,
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
            # Registration.objects.create(
            #     user=user,
            #     department=department,
            #     enrollment_number=enrollment_number if role == 'Student' else None,  # Only save if Student
            #     phone=form.cleaned_data['phone'],
            #     profile_image=form.cleaned_data.get('profile_image'),
            #     role=form.cleaned_data.get('role'),
            #     approved=form.cleaned_data.get('approved')
            # )

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
        if CustomUser.objects.filter(email = get_user).exists() and not User.objects.get(email = get_user).is_active:
            user = CustomUser.objects.get(email= get_user)
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
    recent = News.objects.filter(status='PUBLISH', is_featured=False).order_by('-created')

    news = News.objects.filter(id=id)
    article = get_object_or_404(News, id=id)

    # 🔥 Increment view count
    article.views += 1
    article.save(update_fields=['views'])

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
                reply=comment_text
            )
        else:
            # Save as a main Comment
            Comment.objects.create(news=article, user=request.user, comment=comment_text)

    # Fetch comments along with their replies
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
        "total_comments": total_comments,
        'recent': recent,
        'category': category
    }

    return render(request, "Home/News_Details.html", context)

@login_required(login_url='login')
def LJNews_Detail(request, id):
    # Category Wise Show Posts
    category = Category.objects.annotate(post_count=Count('ljnews'))

    # Recent Post's
    recents = LJNews.objects.filter(status='PUBLISH', is_featured=False).order_by('-created')

    
    ljnews = LJNews.objects.filter(id=id)
    articles = get_object_or_404(LJNews, id=id)

    # 🔥 Increment view count
    articles.views += 1
    articles.save(update_fields=['views'])

    # Check if the user liked the article
    like_this_articles = Likes.objects.filter(user=request.user, news=articles).exists()

    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        comm_id = request.POST.get('comm_id')

        if comm_id:
            # Save as a SubComment (reply)
            parent_comment = get_object_or_404(Comment, id=int(comm_id))
            SubComments.objects.create(
                ljnews=articles,
                user=request.user,
                parent_comment=parent_comment,
                reply=comment_text
            )
        else:
            # Save as a main Comment
            Comment.objects.create(ljnews=articles, user=request.user, comment=comment_text)

    # Fetch comments along with their replies
    comments = [(cm, SubComments.objects.filter(parent_comment=cm)) for cm in Comment.objects.filter(ljnews=articles)]

    form = CommentForm()

    # Comment Count
    total_comments = articles.total_comments()

    context = {
        'articles': articles,
        'like_this_articles': like_this_articles,
        'comments': comments,
        'form': form,
        "total_comments": total_comments,
        'ljnews': ljnews,
        'recents': recents,
        'category': category
    }

    return render(request, "Home/LJNews_Details.html", context)

   

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

@login_required(login_url='login')
def LJlike_post(request, id):
    if request.method == "POST":
        article = get_object_or_404(LJNews, id=id)
        Likes.objects.get_or_create(user=request.user, news=article)
        return redirect(request.META.get('HTTP_REFERER') or 'details')
    return redirect('detail', id=id)

@login_required(login_url='login')
def LJunlike_post(request, id):
    if request.method == "POST":
        article = get_object_or_404(LJNews, id=id)
        Likes.objects.filter(user=request.user, news=article).delete()
        return redirect(request.META.get('HTTP_REFERER') or 'details')
    return redirect('detail', id=id)

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

def LJNEWS(request):
    
    ljnews = LJNews.objects.filter(status='PUBLISH',visibility='APPROVED')
    
    context = {
        'ljnews':ljnews
    }
    
    return render(request, "Home/LJNewz.html", context)

def Gallery(request):
    news = News.objects.filter(status='PUBLISH')
    return render(request, "Home/Gallery.html", {'news':news})

# Admin Dashbord's
@login_required(login_url='login')
def dashboard(request):
    total_news_articles = News.objects.count()
    total_ljnews_articles = LJNews.objects.count()
    total_articles = total_news_articles + total_ljnews_articles

    news_views = News.objects.aggregate(total=Sum('views'))['total'] or 0
    ljnews_views = LJNews.objects.aggregate(total=Sum('views'))['total'] or 0
    total_view = news_views + ljnews_views


    total_comments = Comment.objects.count()

    # Number of Articles per Category
    category_article_counts = defaultdict(int)
    categories = Category.objects.all()
    for category in categories:
        category_article_counts[category.category_name] = News.objects.filter(category=category).count()

    # Prepare data for the bar chart
    bar_labels = list(category_article_counts.keys())
    bar_data = list(category_article_counts.values())

    # Line Chart - Views for last 7 days
    today = now().date( )
    seven_days_ago = today - timedelta()
    date_range = [seven_days_ago + timedelta(days=i) for i in range(7)]

    views_per_day = (
        News.objects
        .filter(created__date__range=(seven_days_ago, today))
        .annotate(date=TruncDate('created'))
        .values('date')
        .annotate(total_views=Sum('views'))
    )

    views_dict = {v['date']: v['total_views'] for v in views_per_day}
    line_labels = [date.strftime('%d %b') for date in date_range]
    line_data = [views_dict.get(date, 0) for date in date_range]


    # Pie Chart - Views by Category
    pie_labels = []
    pie_data = []

    # Loop through each category and get its total views
    for category in categories:
        news_views = News.objects.filter(category=category).aggregate(total=Sum('views'))['total'] or 0
        ljnews_views = LJNews.objects.filter(category=category).aggregate(total=Sum('views'))['total'] or 0
        total_views = news_views + ljnews_views

        if total_views > 0:
            pie_labels.append(category.category_name)
            pie_data.append(total_views)

    context = {
        'total_articles': total_articles,
        'total_views': total_views,
        'total_view':total_view,
        'total_comments': total_comments,
        'line_labels': json.dumps(line_labels),
        'line_data': json.dumps(line_data),
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'bar_labels': json.dumps(bar_labels),
        'bar_data': json.dumps(bar_data),
    }

    return render(request, "Admin/Dashboard.html", context)

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def deletenews(request, id):
    news = News.objects.filter(id=id)
    news.delete()
    messages.success(request, "News/Article deleted successfully!")
    return redirect("addnews")

@login_required(login_url='login')
def AddCategory(request):
    form = CategoryForm()
    categories = Category.objects.filter()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        form.save()
        return redirect("addcategory")
    return render(request,"Admin/AddCategory.html",{'form':form ,'categories':categories})

@login_required(login_url='login')
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

@login_required(login_url='login')
def DeleteCategory(request, id):
    categories = get_object_or_404(Category, pk=id)
    if request.method == 'POST':
        categories.delete()
        messages.success(request, 'Category deleted successfully.')
    return redirect("addcategory")

@login_required(login_url='login')
def Comments(request):
    comments = Comment.objects.all().order_by('-created')  # Latest comments first

    context = {
        'comments': comments,
    }
    return render(request,"Admin/ManageComment.html",context)

def DeleteComment(request, id):
    comment = Comment.objects.filter(id=id)
    comment.delete()
    messages.error(request, "Comment deleted successfully!")
    return redirect("comments")

@login_required(login_url='login')
def ManageUsers(request):
    user_data = User.objects.all()
    user_profile = Profile.objects.all()
    return render(request,"Admin/ManageUsers.html",{'user_data':user_data,'user_profile':user_profile})

def DeleteUser(request, id):
    user = User.objects.filter(id=id)
    user.delete()
    messages.error(request, "User deleted successfully!")
    return redirect("manageusers")

@login_required(login_url='login')
def ManageContact(request):
    contact = Contact.objects.all()
    context = {
        'contact':contact
    }
    return render(request,"Admin/ManageContact.html",context)

def DeleteContact(request, id):
    contact = Contact.objects.filter(id=id)
    contact.delete()
    messages.error(request, "Contact deleted successfully!")
    return redirect("managecontact")

@login_required(login_url='login')
def ManageLJNews(request):
    # Fetch all the LJNews objects, sorted by the latest first
    ljnews = LJNews.objects.all()
    
    # Fetch all categories
    categories = Category.objects.all()

    context = {
        'ljnews': ljnews,
        'categories': categories,
    }

    return render(request, "Admin/ManageLJNews.html", context)

@login_required(login_url='login')
def EditLJNews(request, id):
    ljnews = get_object_or_404(LJNews, id=id)

    if request.method == 'POST':
        form = LJNewsForm(request.POST, request.FILES, instance=ljnews)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.status = ljnews.status  # 👈 preserve original status
            obj.save()
            messages.success(request, "News updated successfully!")
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "Failed to update. Check the form.")
    return redirect('manageljnews')

@login_required(login_url='login')
def DeleteLJNews(request, id):
    # Fetch the article to delete
    ljnews = get_object_or_404(LJNews, id=id)

    # Handle POST request for deletion
    if request.method == 'POST':
        ljnews.delete()  # Delete the article
        messages.success(request, "LJNews/Article deleted successfully!")  # Success message

    return redirect("manageljnews")  # Redirect to the page displaying all LJNews
        
def ManageSliders(request):
    
    sliders = Slider.objects.all().order_by('-created')
    
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES)

        if form.is_valid():
            slider = form.save(commit=False)  # ✅ Get model instance but don't save yet
            slider.save()
            messages.success(request, "Slider/Banner added successfully!")
            return redirect("managesliders")
        else:
            messages.error(request, "Form validation failed. Please check your input.")
    else:
        form = SliderForm()
    
    context = {
        'form': form,
        'sliders':sliders
    }
    
    return render(request, "Admin/ManageSlider.html", context)

def DeleteSlider(request, id):
    slider = Slider.objects.filter(id=id)
    slider.delete()
    messages.success(request, "Slider/Banner deleted successfully!")
    return redirect("managesliders")

def EditSlider(request, id):
    slider = get_object_or_404(Slider, pk=id)

    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES, instance=slider)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.status = slider.status  # 👈 preserve original status
            obj.save()
            messages.success(request, "Slider/Banner updated successfully!")
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "Failed to update. Check the form.")
    return redirect('managesliders')

def ManageGallery(request):
    return render(request, "Admin/ManageGallery.html")


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
            ljnews.author_id = request.user.email  # ✅ Set auther_id field correctly<
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
    ljnews = LJNews.objects.filter(author_id=request.user.email, status='PUBLISH').order_by('-created')
    categories = Category.objects.all()
    
    paginator = Paginator(ljnews, 4)  # Show 2 news per page
    page_number = request.GET.get('page')
    ViewDatafinal = paginator.get_page(page_number)
    context = {
        'ViewDatafinal': ViewDatafinal,  # केवल पेजिनेटेड डेटा भेजें
        'totalPage': range(1, ViewDatafinal.paginator.num_pages + 1),
        'categories': categories,
    }
    return render(request, "Account/ViewPosts.html", context)

def EDITUserPost(request, id):
    ljnews = get_object_or_404(LJNews, id=id)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = LJNewsForm(request.POST, request.FILES, instance=ljnews)
        if form.is_valid():
            form.save()
            messages.success(request, "News updated successfully!")
            return redirect('posts')
    else:
        form = LJNewsForm(instance=ljnews)

    return render(request, 'Account/PostArticle.html', {
        'form': form,
        'ljnews': ljnews,
        'categories': categories
    })
    
def DeleteUserPost(request, id):
    ljnews = get_object_or_404(LJNews,id=id)
    if request.method == 'POST':
        ljnews.delete()
    messages.success(request, "News/Article deleted successfully!")
    return redirect("posts")
import json
import random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from ApaniNews import settings
from ApaniNewz.forms import CategoryForm, CommentForm, ContactForm, LJNewsForm, LoginForm, NewsForm, ProfileUpdateForm, RegistrationForm, SliderForm, SubCommentForm, UserUpdate
from .models import Category, Contact, LJNews, Likes, News, Registration, Profile,Comment, Slider,SubComments, UserOTP
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
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils.timezone import now, timedelta
from collections import defaultdict
# Create your views here.


@login_required(login_url='login')
def home(request):  
    
    # Slider
    # slider = LJNews.objects.filter(status='PUBLISH', visibility='APPROVED')
    slider = Slider.objects.filter(status='PUBLISH').order_by('-created')  # Get the latest 5 sliders
    
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
    ljnews = None
    catid = request.GET.get('category')
    if catid:
        ljnews = LJNews.get_all_ljnews_byID(catid)
    else:
        ljnews = LJNews.objects.filter(status='PUBLISH',visibility='APPROVED').order_by('-created')
    
        
    context = {
        'categories':categories,
        'news': news,
        'ljnews':ljnews,
        'trending':trending,
        'featured':featured,
        'cat_news':cat_news,
        'slider':slider
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
                print(form.errors)
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
                    user.approved = 'NOT APPROVED'  # Ensure user is 'NOT APPROVED' until verified
                    user.save()
                    login(request, user)
                    messages.success(request, "Your account has been successfully verified and logged in.")
                    return redirect('login')
                else:
                    messages.error(request, "Invalid OTP. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "No user found for verification.")

            return render(request, "Home/Registration.html", {'OTP': True, 'user': email})

        # Registration Form Handling
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Account not active until OTP verification
            user.approved = 'NOT APPROVED'  # Default to 'NOT APPROVED'
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
                fail_silently=False,
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
            # Registration.objects.create(
            #     user=user,
            #     department=department,
            #     enrollment_number=enrollment_number if role == 'Student' else None,  # Only save if Student
            #     phone=form.cleaned_data['phone'],
            #     profile_image=form.cleaned_data.get('profile_image'),
            #     role=form.cleaned_data.get('role'),
            #     approved=form.cleaned_data.get('approved')
            # )

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
    recent = News.objects.filter(status='PUBLISH', is_featured=False).order_by('-created')

    news = News.objects.filter(id=id)
    article = get_object_or_404(News, id=id)

    # 🔥 Increment view count
    article.views += 1
    article.save(update_fields=['views'])

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
                reply=comment_text
            )
        else:
            # Save as a main Comment
            Comment.objects.create(news=article, user=request.user, comment=comment_text)

    # Fetch comments along with their replies
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
        "total_comments": total_comments,
        'recent': recent,
        'category': category
    }

    return render(request, "Home/News_Details.html", context)

@login_required(login_url='login')
def LJNews_Detail(request, id):
    # Category Wise Show Posts
    category = Category.objects.annotate(post_count=Count('ljnews'))

    # Recent Post's
    recents = LJNews.objects.filter(status='PUBLISH', is_featured=False).order_by('-created')

    
    ljnews = LJNews.objects.filter(id=id)
    articles = get_object_or_404(LJNews, id=id)

    # 🔥 Increment view count
    articles.views += 1
    articles.save(update_fields=['views'])

    # Check if the user liked the article
    like_this_articles = Likes.objects.filter(user=request.user, news=articles).exists()

    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        comm_id = request.POST.get('comm_id')

        if comm_id:
            # Save as a SubComment (reply)
            parent_comment = get_object_or_404(Comment, id=int(comm_id))
            SubComments.objects.create(
                ljnews=articles,
                user=request.user,
                parent_comment=parent_comment,
                reply=comment_text
            )
        else:
            # Save as a main Comment
            Comment.objects.create(ljnews=articles, user=request.user, comment=comment_text)

    # Fetch comments along with their replies
    comments = [(cm, SubComments.objects.filter(parent_comment=cm)) for cm in Comment.objects.filter(ljnews=articles)]

    form = CommentForm()

    # Comment Count
    total_comments = articles.total_comments()

    context = {
        'articles': articles,
        'like_this_articles': like_this_articles,
        'comments': comments,
        'form': form,
        "total_comments": total_comments,
        'ljnews': ljnews,
        'recents': recents,
        'category': category
    }

    return render(request, "Home/LJNews_Details.html", context)

   

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

@login_required(login_url='login')
def LJlike_post(request, id):
    if request.method == "POST":
        article = get_object_or_404(LJNews, id=id)
        Likes.objects.get_or_create(user=request.user, news=article)
        return redirect(request.META.get('HTTP_REFERER') or 'details')
    return redirect('detail', id=id)

@login_required(login_url='login')
def LJunlike_post(request, id):
    if request.method == "POST":
        article = get_object_or_404(LJNews, id=id)
        Likes.objects.filter(user=request.user, news=article).delete()
        return redirect(request.META.get('HTTP_REFERER') or 'details')
    return redirect('detail', id=id)

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

def LJNEWS(request):
    
    ljnews = LJNews.objects.filter(status='PUBLISH',visibility='APPROVED')
    
    context = {
        'ljnews':ljnews
    }
    
    return render(request, "Home/LJNewz.html", context)

def Gallery(request):
    news = News.objects.filter(status='PUBLISH')
    return render(request, "Home/Gallery.html", {'news':news})

# Admin Dashbord's
@login_required(login_url='login')
def dashboard(request):
    total_news_articles = News.objects.count()
    total_ljnews_articles = LJNews.objects.count()
    total_articles = total_news_articles + total_ljnews_articles

    news_views = News.objects.aggregate(total=Sum('views'))['total'] or 0
    ljnews_views = LJNews.objects.aggregate(total=Sum('views'))['total'] or 0
    total_view = news_views + ljnews_views


    total_comments = Comment.objects.count()

    # Number of Articles per Category
    category_article_counts = defaultdict(int)
    categories = Category.objects.all()
    for category in categories:
        category_article_counts[category.category_name] = News.objects.filter(category=category).count()

    # Prepare data for the bar chart
    bar_labels = list(category_article_counts.keys())
    bar_data = list(category_article_counts.values())

    # Line Chart - Views for last 7 days
    today = now().date( )
    seven_days_ago = today - timedelta()
    date_range = [seven_days_ago + timedelta(days=i) for i in range(7)]

    views_per_day = (
        News.objects
        .filter(created__date__range=(seven_days_ago, today))
        .annotate(date=TruncDate('created'))
        .values('date')
        .annotate(total_views=Sum('views'))
    )

    views_dict = {v['date']: v['total_views'] for v in views_per_day}
    line_labels = [date.strftime('%d %b') for date in date_range]
    line_data = [views_dict.get(date, 0) for date in date_range]


    # Pie Chart - Views by Category
    pie_labels = []
    pie_data = []

    # Loop through each category and get its total views
    for category in categories:
        news_views = News.objects.filter(category=category).aggregate(total=Sum('views'))['total'] or 0
        ljnews_views = LJNews.objects.filter(category=category).aggregate(total=Sum('views'))['total'] or 0
        total_views = news_views + ljnews_views

        if total_views > 0:
            pie_labels.append(category.category_name)
            pie_data.append(total_views)

    context = {
        'total_articles': total_articles,
        'total_views': total_views,
        'total_view':total_view,
        'total_comments': total_comments,
        'line_labels': json.dumps(line_labels),
        'line_data': json.dumps(line_data),
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'bar_labels': json.dumps(bar_labels),
        'bar_data': json.dumps(bar_data),
    }

    return render(request, "Admin/Dashboard.html", context)

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def deletenews(request, id):
    news = News.objects.filter(id=id)
    news.delete()
    messages.success(request, "News/Article deleted successfully!")
    return redirect("addnews")

@login_required(login_url='login')
def AddCategory(request):
    form = CategoryForm()
    categories = Category.objects.filter()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        form.save()
        return redirect("addcategory")
    return render(request,"Admin/AddCategory.html",{'form':form ,'categories':categories})

@login_required(login_url='login')
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

@login_required(login_url='login')
def DeleteCategory(request, id):
    categories = get_object_or_404(Category, pk=id)
    if request.method == 'POST':
        categories.delete()
        messages.success(request, 'Category deleted successfully.')
    return redirect("addcategory")

@login_required(login_url='login')
def Comments(request):
    comments = Comment.objects.all().order_by('-created')  # Latest comments first

    context = {
        'comments': comments,
    }
    return render(request,"Admin/ManageComment.html",context)

def DeleteComment(request, id):
    comment = Comment.objects.filter(id=id)
    comment.delete()
    messages.error(request, "Comment deleted successfully!")
    return redirect("comments")

@login_required(login_url='login')
def ManageUsers(request):
    user_data = User.objects.all()
    user_profile = Profile.objects.all()
    return render(request,"Admin/ManageUsers.html",{'user_data':user_data,'user_profile':user_profile})

def DeleteUser(request, id):
    user = User.objects.filter(id=id)
    user.delete()
    messages.error(request, "User deleted successfully!")
    return redirect("manageusers")

@login_required(login_url='login')
def ManageContact(request):
    contact = Contact.objects.all()
    context = {
        'contact':contact
    }
    return render(request,"Admin/ManageContact.html",context)

def DeleteContact(request, id):
    contact = Contact.objects.filter(id=id)
    contact.delete()
    messages.error(request, "Contact deleted successfully!")
    return redirect("managecontact")

@login_required(login_url='login')
def ManageLJNews(request):
    # Fetch all the LJNews objects, sorted by the latest first
    ljnews = LJNews.objects.all()
    
    # Fetch all categories
    categories = Category.objects.all()

    context = {
        'ljnews': ljnews,
        'categories': categories,
    }

    return render(request, "Admin/ManageLJNews.html", context)

@login_required(login_url='login')
def EditLJNews(request, id):
    ljnews = get_object_or_404(LJNews, id=id)

    if request.method == 'POST':
        form = LJNewsForm(request.POST, request.FILES, instance=ljnews)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.status = ljnews.status  # 👈 preserve original status
            obj.save()
            messages.success(request, "News updated successfully!")
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "Failed to update. Check the form.")
    return redirect('manageljnews')

@login_required(login_url='login')
def DeleteLJNews(request, id):
    # Fetch the article to delete
    ljnews = get_object_or_404(LJNews, id=id)

    # Handle POST request for deletion
    if request.method == 'POST':
        ljnews.delete()  # Delete the article
        messages.success(request, "LJNews/Article deleted successfully!")  # Success message

    return redirect("manageljnews")  # Redirect to the page displaying all LJNews
        
def ManageSliders(request):
    
    sliders = Slider.objects.all().order_by('-created')
    
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES)

        if form.is_valid():
            slider = form.save(commit=False)  # ✅ Get model instance but don't save yet
            slider.save()
            messages.success(request, "Slider/Banner added successfully!")
            return redirect("managesliders")
        else:
            messages.error(request, "Form validation failed. Please check your input.")
    else:
        form = SliderForm()
    
    context = {
        'form': form,
        'sliders':sliders
    }
    
    return render(request, "Admin/ManageSlider.html", context)

def DeleteSlider(request, id):
    slider = Slider.objects.filter(id=id)
    slider.delete()
    messages.success(request, "Slider/Banner deleted successfully!")
    return redirect("managesliders")

def EditSlider(request, id):
    slider = get_object_or_404(Slider, pk=id)

    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES, instance=slider)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.status = slider.status  # 👈 preserve original status
            obj.save()
            messages.success(request, "Slider/Banner updated successfully!")
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "Failed to update. Check the form.")
    return redirect('managesliders')

def ManageGallery(request):
    return render(request, "Admin/ManageGallery.html")


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
            ljnews.author_id = request.user.email  # ✅ Set auther_id field correctly<
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
    ljnews = LJNews.objects.filter(author_id=request.user.email, status='PUBLISH').order_by('-created')
    categories = Category.objects.all()
    
    paginator = Paginator(ljnews, 4)  # Show 2 news per page
    page_number = request.GET.get('page')
    ViewDatafinal = paginator.get_page(page_number)
    context = {
        'ViewDatafinal': ViewDatafinal,  # केवल पेजिनेटेड डेटा भेजें
        'totalPage': range(1, ViewDatafinal.paginator.num_pages + 1),
        'categories': categories,
    }
    return render(request, "Account/ViewPosts.html", context)

def EDITUserPost(request, id):
    ljnews = get_object_or_404(LJNews, id=id)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = LJNewsForm(request.POST, request.FILES, instance=ljnews)
        if form.is_valid():
            form.save()
            messages.success(request, "News updated successfully!")
            return redirect('posts')
    else:
        form = LJNewsForm(instance=ljnews)

    return render(request, 'Account/PostArticle.html', {
        'form': form,
        'ljnews': ljnews,
        'categories': categories
    })
    
def DeleteUserPost(request, id):
    ljnews = get_object_or_404(LJNews,id=id)
    if request.method == 'POST':
        ljnews.delete()
    messages.success(request, "News/Article deleted successfully!")
    return redirect("posts")