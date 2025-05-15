from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from app.models import Item
from .models import User, Staff, Administrator
from .forms import StaffLoginForm, AdminLoginForm
from django.contrib import messages
from django.contrib.auth import logout

# Create your views here.

@login_required
def additemform(request):
    context = {
        'title': 'Add Item Form',
        'year': datetime.now().year,
    }
    context['user'] = request.user

    return render(request,'additem/additemform.html',context)

def additemconfirmation(request):

    newitem_id = request.POST['item_id']
    newitem_name= request.POST['item_name']
    newitem_description = request.POST['item_description']

    newitem = Item(item_id = newitem_id,item_name = newitem_name, item_description =
        newitem_description)
    newitem.save()

    context = {

        'item_id': newitem_id,
        'item_name': newitem_name,
        'item_description': newitem_description,
    }
    return render(request,'additem/additemconfirmation.html',context)

def choose_role(request):
    return render(request, 'additem/choose_role.html')

def staff_login(request):
    if request.method == 'POST':
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.staff_password = form.cleaned_data['password']
            staff.save()
            messages.success(request, 'Staff login successful!')
            return redirect('dashboard')
    else:
        form = StaffLoginForm()
    return render(request, 'additem/login.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            admin.admin_password = form.cleaned_data['password']
            admin.save()
            messages.success(request, 'Admin login successful!')
            return redirect('dashboard')
    else:
        form = AdminLoginForm()
    return render(request, 'additem/login.html', {'form': form})

def home(request):
    """Renders the home page."""
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def register(request):
    """Renders the registration page."""
    return render(
        request,
        'app/register.html',
        {
            'title':'Register',
            'year':datetime.now().year,
        }
    )

def login_view(request):
    """Renders the login page."""
    return render(
        request,
        'app/login.html',
        {
            'title':'Login',
            'year':datetime.now().year,
        }
    )

def logout_view(request):
    """Handles logout for both Parent and Tutor."""
    
    # Check if the user is a parent or tutor
    if hasattr(request.user, 'parent'):
        # Render the logout confirmation page for the parent
        if request.method == 'POST':
            logout(request)
            messages.success(request, 'You have been logged out successfully.')
            return redirect('app:home')
        return render(request, 'app/parent_logout.html')

    elif hasattr(request.user, 'tutor'):
        # Render the logout confirmation page for the tutor
        if request.method == 'POST':
            logout(request)
            messages.success(request, 'You have been logged out successfully.')
            return redirect('app:home')
        return render(request, 'app/tutor_logout.html')

    # If the user is neither a parent nor tutor, log them out immediately
    logout(request)
    return redirect('app:home')