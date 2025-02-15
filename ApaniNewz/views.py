from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from ApaniNewz.forms import CategoryForm, LoginForm, NewsForm, RegistrationForm
from .models import Category, News, Registration, Profile
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Create your views here.

def home(request):
    return render(request, 'Home/index.html')

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

# def register_view(request):
#     if request.user.is_authenticated:
#         return redirect('index')

#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)  # Handle file uploads
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])  # Hash the password
#             user.is_active = True
#             user.save()

#             messages.success(request, "Your account was successfully created.")
#             login(request, user)  # Log the user in after registration
#             return redirect('login')  # Redirect to home page after successful registration

#     else:
#         form = RegistrationForm()
#     return render(request,"Home/Registration.html",{'form':form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            user = form.save(commit=False)  # Save user but don't commit yet
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.is_active = True  # Activate user immediately (change if using OTP)
            user.save()

            # Save additional fields in Profile model
            cost =Profile.objects.create(
                user=user,
                enrollment_number=form.cleaned_data['enrollment_number'],
                phone=form.cleaned_data['phone'],
                profile_image=form.cleaned_data.get('profile_image')
            )
            cost.save()
            messages.success(request, "Your account was successfully created.")
            login(request, user)  # Log in the user after registration
            return redirect('index')  # Redirect to homepage after successful registration

    else:
        form = RegistrationForm()
    
    return render(request, "Home/Registration.html", {'form': form})

def News_Detail(request):
    return render(request, "Home/News_Details.html")

def Contact(request):
    return render(request, "Home/Contact.html")

def About(request):
    return render(request, "Home/About.html")

def Categories(request):
    categories = Category.objects.filter()
    nws = None
    CATID = request.GET.get('category')
    if CATID:
        nws = News.get_all_product_byID(CATID)
    else:
        nws = News.objects.filter(status='PUBLISH')
    return render(request, "Home/Category.html",{'categories':categories,'nws':nws})
    
def LatestNewz(request):
    return render(request, "Home/LatestNewz.html")

# Admin Dashbord's
def dashboard(request):
    return render(request,"Admin/Dashboard.html")

def AddNews(request):
    article = News.objects.all()
    categories = Category.objects.all()

    if request.method == 'POST':
        form = NewsForm(request.POST)  # Bind form for content field

        if form.is_valid():  # ✅ Validate form before accessing cleaned_data
            content = form.cleaned_data.get("content")  # ✅ Correct way to access cleaned data

            # Manually retrieve other fields
            title = request.POST.get("title")
            sub_title = request.POST.get("sub_title")
            cat = request.POST.get("category")
            catOBJ = Category.objects.get(id=cat)  # Fetch category object
            author = request.POST.get("author")
            status = request.POST.get("status")
            if 'news_image' in request.FILES:
                news_image = request.FILES['news_image']
            else:
                news_image = None   # Handle file uploads safely

            # Create and save the news entry
            news = News(
                title=title,
                sub_title=sub_title,
                category=catOBJ,
                author=author,
                content=content,  # ✅ Corrected content retrieval
                status=status,
                news_image=news_image,
            )
            news.save()

            messages.success(request, "News/Article added successfully!")
            return redirect("addnews")
        else:
            messages.error(request, "Form validation failed. Please check your input.")

    else:
        form = NewsForm()

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
    return render(request,"Admin/ManageComment.html")

def ManageUsers(request):
    user_data = User.objects.all()
    user_profile = Profile.objects.all()
    return render(request,"Admin/ManageUsers.html",{'user_data':user_data,'user_profile':user_profile})

def ManageContact(request):
    return render(request,"Admin/ManageContact.html")

# Account's Details

def ProfilePage(request):
    return render(request, "Account/Profile.html")

def PostArticle(request):
    categories = Category.objects.all()
    form = NewsForm()
    return render(request,"Account/PostArticle.html",{"categories":categories,'form':form})

def Posts(request):
    return render(request,"Account/Posts.html")