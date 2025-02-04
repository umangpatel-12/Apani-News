from django.contrib import admin
from django.urls import include, path
from ApaniNewz import views

urlpatterns = [
    path('', views.home, name= 'index'),
    path('login', views.login_view, name= 'login'),
    path('accounts/logout',views.logout_view, name='logout'),
    path('Registration', views.register_view, name= 'registration'),
    
    path('Details', views.News_Detail, name= 'details'),
    path('Contact', views.Contact, name= 'contact'),
    path('About', views.About, name= 'about'),
    path('Category', views.Categories, name= 'category'),
    path('Latest-News', views.LatestNewz, name= 'latestnews'),
    path('Profile', views.ProfilePage, name= 'profile'),



    # Admin Side
    path('Dashboard',views.dashboard,name='dashboard'),
    path('Add-News-Articles',views.AddNews,name='addnews'),
    path('AddCategory',views.AddCategory,name='addcategory'),
    path('Comments',views.Comments,name='comments'),
    path('Manage-Contacts',views.ManageContact,name='contacts'),
    path('Manage-Users',views.ManageUsers,name='users'),

]