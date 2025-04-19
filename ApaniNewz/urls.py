from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from ApaniNews import settings
from ApaniNewz import views
from .views import ResendOTP

urlpatterns = [
    path('', views.home, name= 'index'),
    path('login', views.login_view, name= 'login'),
    path('accounts/logout',views.logout_view, name='logout'),
    path('Registration', views.register_view, name= 'registration'),
    path('resend-otp', ResendOTP),
    
    path('Details/<int:id>', views.News_Detail, name= 'details'),
    path('Detail/<int:id>/', views.LJNews_Detail, name='detail'),
    path('Contact', views.Contacts, name= 'contact'),
    path('About', views.About, name= 'about'),
    path('Category/', views.Categories, name= 'category'),
    path('Latest-News', views.LatestNewz, name= 'latestnews'),
    path('Category/Search/', views.CategorySearch, name= 'category_search'),

    # Account's
    path('Profile', views.ProfilePage, name= 'profile'),
    # path('Edit-Profile', views.EditProfile, name= 'edit_profile'),
    path('Post-Article', views.PostArticle, name= 'post_article'),
    path('Edit-Post/<int:id>', views.EDITUserPost, name= 'editpost'),
    path('Delete-Post/<int:id>', views.DeleteUserPost, name= 'deletepost'),
    path('View-Posts/', views.Posts, name= 'posts'),
    path('like/<int:id>/', views.like_post, name='like_post'),
    path('unlike/<int:id>/', views.unlike_post, name='unlike_post'),
    path('LJlike/<int:id>/', views.LJlike_post, name='ljlike_post'),
    path('LJunlike/<int:id>/', views.LJunlike_post, name='ljunlike_post'),
    path('Article/Search/', views.Search_View,name='search'),
    



    # Admin Side
    path('Dashboard',views.dashboard,name='dashboard'),
    path('Add-News-Articles',views.AddNews,name='addnews'),
    path('Edit-News/<int:id>',views.EDITNews,name='editnews'),
    path('Delete-News/<int:id>/', views.deletenews, name='deletenews'),
    path('AddCategory',views.AddCategory,name='addcategory'),
    path('Edit-Category/<int:id>', views.EditCategory, name='editcategory'),
    path('Delete-Category/<int:id>', views.DeleteCategory, name='deletecategory'),
    path('Comments',views.Comments,name='comments'),
    path('Manage-Contacts',views.ManageContact,name='contacts'),
    path('Manage-Users',views.ManageUsers,name='users'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)