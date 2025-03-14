import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import requests
from django.core.exceptions import ValidationError
from ApaniNewz.models import Comment, LJNews, Profile, Registration,News,Category, SubComments
from ckeditor.widgets import CKEditorWidget

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'id': 'email',
            'name': 'email',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email'
        }),
        max_length=254,
        required=True
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'name': 'password',
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        }),
        required=True,
        min_length=6
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email does not exist.")
        return email

class RegistrationForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('Choose Role', 'Choose Role'),
        ('Student', 'Student'),
        ('Faculty/Staff', 'Faculty/Staff'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'id': 'role',
            'name': 'role',
            'class': 'form-select form-select-lg',
            'onchange': 'this.form.submit();'
        })
    )

    enrollment_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'enrollment_number',
            'name': 'enrollment_number',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enrollment Number'
        }),
        max_length=12,
        required= False
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'username',
            'name': 'username',
            'class': 'form-control form-control-lg',
            'placeholder': 'Username'
        }),
        max_length=150,
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'id': 'email',
            'name': 'email',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email'
        }),
        max_length=254,
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'name': 'password',
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        }),
        required=True,
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'confirm_password',
            'name': 'confirm_password',
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm Password'
        }),
        required=True
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'first_name',
            'name': 'first_name',
            'class': 'form-control form-control-lg',
            'placeholder': 'First Name'
        }),
        max_length=50,
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'last_name',
            'name': 'last_name',
            'class': 'form-control form-control-lg',
            'placeholder': 'Last Name'
        }),
        max_length=50,
        required=True
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'phone',
            'name': 'phone',
            'class': 'form-control form-control-lg',
            'placeholder': 'Phone Number'
        }),
        max_length=10,  # Adjust as needed for phone number length
        required=True
    )
    profile_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'id': 'profile_image',
            'name': 'profile_image',
            'class': 'form-control form-control-lg'
        }),
        required=False  # Set to `True` if profile image is mandatory
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone', 'profile_image', 'enrollment_number', 'role']


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     # Remove enrollment_number if the selected role is Faculty/Staff
    #     if self.data.get('role') == 'Faculty/Staff':
    #         self.fields.pop('enrollment_number')

    # def clean(self):
    #     cleaned_data = super().clean()
    #     role = cleaned_data.get('role')
    #     enrollment_number = cleaned_data.get('enrollment_number')

    #     # If role is "Student", enrollment_number is required
    #     if role == 'Student' and not enrollment_number:
    #         self.add_error('enrollment_number', 'Enrollment number is required for students.')

    #     return cleaned_data
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove enrollment_number if role is Faculty/Staff
        if 'role' in self.data and self.data['role'] == 'Faculty/Staff':
            self.fields.pop('enrollment_number')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        enrollment_number = cleaned_data.get('enrollment_number')

        # If role is "Student", enrollment_number is required
        if role == 'Student' and not enrollment_number:
            self.add_error('enrollment_number', 'Enrollment number is required for students.')

        return cleaned_data


    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username is already taken.")

        # Ensure username contains only alphabets and optionally underscores or hyphens
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
            raise ValidationError("Username should start with a letter and can only contain letters, numbers, underscores, or hyphens.")

        # Ensure username does not contain consecutive special characters (e.g., "__" or "--")
        if re.search(r'[_-]{2,}', username):
            raise ValidationError("Username should not contain consecutive underscores or hyphens.")

        return username

    def clean_first_name(self):
        widget =forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise forms.ValidationError("First name should only contain letters.")
        if len(first_name) < 3:
            raise forms.ValidationError("First name must be at least 2 characters long.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise forms.ValidationError("Last name should only contain letters.")
        if len(last_name) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters long.")
        return last_name

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Please use a valid email address")
        return email
    
     # Phone number validation
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        # Ensure the phone number contains only digits
        if not phone.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        
        # Ensure the phone number length is exactly 10 digits (adjust if needed)
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits long.")
        
        return phone
        
    def clean_enrollment_number(self):
        enrollment_number = self.cleaned_data.get('enrollment_number')

        # Check if the enrollment number already exists in the Registration model
        if Registration.objects.filter(enrollment_number=enrollment_number).exists():
            raise forms.ValidationError("This enrollment number is already registered.")

        return enrollment_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash password before saving

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                enrollment_number=self.cleaned_data["enrollment_number"],
                phone=self.cleaned_data["phone"],
                profile_image=self.cleaned_data.get("profile_image")
            )

        return user

class NewsForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'title',
            'name': 'title',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter News Title'
        }),
        max_length=255,
        required=True
    )

    sub_title = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'sub_title',
            'name': 'sub_title',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Sub Title'
        }),
        max_length=255,
        required=True
    )

    author = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'author',
            'name': 'author',
            'class': 'form-control form-control-lg',
            'placeholder': 'Author Name'
        }),
        max_length=50,
        required=True
    )

    content = forms.CharField(
        widget=CKEditorWidget(attrs={
            'id': 'content',
            'name': 'content',
            'class': 'form-control',
            'placeholder': 'Write your news content here...'
        }),
        required=False
    )

    status = forms.ChoiceField(
        choices=News.STATUS,
        widget=forms.Select(attrs={
            'id': 'status',
            'name': 'status',
            'class': 'form-select form-select-lg'
        })
    )

    news_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'id': 'image',
            'name': 'image',
            'class': 'form-control'
        }),
        required=False
    )

    is_featured = forms.BooleanField(
    widget=forms.CheckboxInput(attrs={
        'id': 'is_featured',
        'name': 'is_featured',
        'class': 'custom-checkbox'
    }),
    required=False,  # ✅ Ensure unchecked state is handled as False
    initial=False
)

    class Meta:
        model = News
        fields = ['title', 'sub_title', 'category', 'author', 'content', 'status', 'news_image','is_featured']
        widgets = {
            'category': forms.Select(attrs={
                'id': 'category',
                'name': 'category',
                'class': 'form-select form-select-lg'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from the view
        super().__init__(*args, **kwargs)
        if user:
            self.fields['author'] = forms.CharField(
                initial=f"{user.first_name} {user.last_name}", 
                widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control form-control-lg'})
            )

class LJNewsForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'title',
            'name': 'title',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter News Title'
        }),
        max_length=255,
        required=True
    )

    sub_title = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'sub_title',
            'name': 'sub_title',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Sub Title'
        }),
        max_length=255,
        required=True
    )

    author = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'author',
            'name': 'author',
            'class': 'form-control form-control-lg',
            'placeholder': 'Author Name'
        }),
        max_length=50,
        required=True
    )

    content = forms.CharField(
        widget=CKEditorWidget(attrs={
            'id': 'content',
            'name': 'content',
            'class': 'form-control',
            'placeholder': 'Write your news content here...'
        }),
        required=False
    )

    status = forms.ChoiceField(
        choices=News.STATUS,
        widget=forms.Select(attrs={
            'id': 'status',
            'name': 'status',
            'class': 'form-select form-select-lg'
        })
    )

    ljnews_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'id': 'image',
            'name': 'image',
            'class': 'form-control'
        }),
        required=False
    )
    
    is_featured = forms.BooleanField(
    widget=forms.CheckboxInput(attrs={
        'id': 'is_featured',
        'name': 'is_featured',
        'class': 'custom-checkbox'
    }),
    required=False,  # ✅ Ensure unchecked state is handled as False
    initial=False
)

    class Meta:
        model = LJNews
        fields = ['title', 'sub_title', 'category', 'author', 'content', 'status', 'ljnews_image','is_featured']
        widgets = {
            'category': forms.Select(attrs={
                'id': 'category',
                'name': 'category',
                'class': 'form-select form-select-lg'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from the view
        super().__init__(*args, **kwargs)
        if user:
            self.fields['author'] = forms.CharField(
                initial=f"{user.first_name} {user.last_name}", 
                widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control form-control-lg'})
            )

class CategoryForm(forms.ModelForm):
    category_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'category',
            'name': 'Category Name',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Category Name'
        }),
        max_length=255,
        required=True
    )

    class Meta:
        model = Category
        fields = ['category_name']

    def clean_categoryname(self):
        category_name = self.cleaned_data.get('Category Name')
        if Category.objects.filter(category_name=category_name).exists():
            raise forms.ValidationError("Category with this name already exists.")
        return category_name
   
class UserUpdate(forms.ModelForm):

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'first_name',
            'name': 'first_name',
            'class': 'form-control form-control-lg',
            'placeholder': 'First Name'
        }),
        max_length=50,
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'last_name',
            'name': 'last_name',
            'class': 'form-control form-control-lg',
            'placeholder': 'Last Name'
        }),
        max_length=50,
        required=True
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'username',
            'name': 'username',
            'class': 'form-control form-control-lg',
            'placeholder': 'Username'
        }),
        max_length=150,
        disabled=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'id': 'email',
            'name': 'email',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email'
        }),
        max_length=254,
        disabled=True
        # required=True
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Faculty/Staff', 'Faculty/Staff'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'id': 'role',
            'name': 'role',
            'class': 'form-select form-select-lg',
            'onchange': 'this.form.submit();'
        }),
        disabled=True
    )
    
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'phone',
            'name': 'phone',
            'class': 'form-control form-control-lg',
            'placeholder': 'Phone Number'
        }),
        max_length=15,
        required=True
    )

    gender = forms.ChoiceField(
        choices=Profile.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'id': 'gender',
            'name': 'gender',
            'class': 'form-select form-select-lg'
        })
    )

    enrollment_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'enrollment_number',
            'name': 'enrollment_number',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enrollment Number'
        }),
        max_length=12,
        disabled=True
        # required=True
    )

    profile_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'id': 'profile_image',
            'name': 'profile_image',
            'class': 'form-control'
        }),
        required=False
    )

    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'bio',
            'name': 'bio',
            'class': 'form-control',
            'placeholder': 'Enter your bio'
        }),
        max_length=125,
        required=False
    )

    location = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'location',
            'name': 'location',
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your location'
        }),
        max_length=30,
        required=False
    )
    class Meta:
        model = Profile
        fields = ['phone', 'gender','enrollment_number','role' ,'profile_image', 'bio', 'location']

class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'comment',
            'name': 'comment',
            'rows': '2',
            'class': 'form-control form-control-lg',
            'placeholder': 'Write your comment here...'
        }),
    )

    class Meta:
        model = Comment
        fields = ['comment']

class SubCommentForm(forms.ModelForm):
    reply = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'reply',
            'name': 'reply',
            'rows': '2',
            'class': 'form-control form-control-lg',
            'placeholder': 'Write your reply here...'
        }),
    
    )

    class Meta:
        model = SubComments
        fields = ['reply']

