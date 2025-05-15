from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, JsonResponse
from django.template import RequestContext
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum, Case, When, IntegerField, Value, F
from django.db import transaction
from additem.models import (
    User, Parent, Tutor, Schedule, Booking, 
    Payment, Class, FavoriteTutor, SupportAssistance,
    Communication, Feedback, Notification, UserNotification
)
import logging
import json
import platform
import django

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year': datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Dr. Yeoh.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'Online Private Tutor Finder System',
            'message':'This application helps students find private tutors based on their needs and preferences.',
            'year':datetime.now().year,
        }
    )

@login_required
def menu(request):
    check_employee = request.user.groups.filter(name='employee').exists()

    context = {
            'title':'Main Menu',
            'is_employee': check_employee,
            'year':datetime.now().year,
        }
    context['user'] = request.user

    return render(request,'app/menu.html',context)

def role_select(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'parent':
            return redirect('app:register_parent')
        elif role == 'tutor':
            return redirect('app:register_tutor')
    return render(request, 'app/role_select.html')

@transaction.atomic
def register_parent(request):
    if request.method == 'POST':
        try:
            # Get form data
            username = request.POST.get('username')  # This will be used as both username and full_name
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            child_name = request.POST.get('child_name')
            child_age = request.POST.get('child_age')
            child_level = request.POST.get('child_level')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            print("\n=== Registration Data ===")
            print(f"Username/Full Name: {username}")
            print(f"Email: {email}")

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return render(request, 'app/register_parent.html')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
                return render(request, 'app/register_parent.html')

            # Generate user_id for internal use
            try:
                last_parent = User.objects.filter(user_role='PARENT').order_by('-user_id').first()
                if not last_parent:
                    next_id = 'P001'
                else:
                    last_num = int(last_parent.user_id[1:])
                    next_id = f'P{(last_num + 1):03d}'
            except Exception as e:
                print(f"Error generating ID: {str(e)}")
                next_id = 'P001'

            # Create the user with username as full name
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_id=next_id,
                user_phone_num=contact_number,
                first_name=username.split()[0] if ' ' in username else username,
                last_name=username.split()[-1] if ' ' in username else '',
                user_role='PARENT',
                profile_status='ACTIVE'  # Set parent status to ACTIVE immediately
            )

            # Create parent profile using username as parent_name
            parent = Parent.objects.create(
                user=user,
                parent_name=username,  # Use username as parent_name
                child_name=child_name,
                child_age=int(child_age),
                child_level=child_level
            )

            messages.success(request, "Registration successful! Please login with your username and password.")
            return redirect('app:login')

        except Exception as e:
            print(f"Registration failed: {str(e)}")
            messages.error(request, str(e))
            return render(request, 'app/register_parent.html')

    return render(request, 'app/register_parent.html')

@transaction.atomic
def register_tutor(request):
    if request.method == 'POST':
        try:
            # Get form data
            username = request.POST.get('username')  # This will be used as tutor's full name
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            education_level = request.POST.get('education_level')
            subject_taught = request.POST.get('subject_taught')
            certificate = request.FILES.get('certificate')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            print("\n=== Registration Data ===")
            print(f"Username/Full Name: {username}")
            print(f"Email: {email}")

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return render(request, 'app/register_tutor.html')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
                return render(request, 'app/register_tutor.html')

            # Generate tutor_id
            try:
                last_tutor = User.objects.filter(user_role='TUTOR').order_by('-user_id').first()
                if not last_tutor:
                    next_id = 'T001'
                else:
                    last_num = int(last_tutor.user_id[1:])
                    next_id = f'T{(last_num + 1):03d}'
            except Exception as e:
                print(f"Error generating ID: {str(e)}")
                next_id = 'T001'

            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_id=next_id,
                user_phone_num=contact_number,
                first_name=username.split()[0] if ' ' in username else username,
                last_name=username.split()[-1] if ' ' in username else '',
                user_role='TUTOR',
                profile_status='PENDING'
            )

            # Create tutor profile
            tutor = Tutor.objects.create(
                user=user,
                tutor_name=username,
                education_level=education_level,
                subject_taught=subject_taught,
                certificate=certificate
            )

            messages.success(request, "Registration successful! Please login with your username and password.")
            return redirect('app:login')

        except Exception as e:
            print(f"Registration failed: {str(e)}")
            messages.error(request, str(e))
            return render(request, 'app/register_tutor.html')

    return render(request, 'app/register_tutor.html')

def register(request):
    role = request.GET.get('role')
    if not role:
        return redirect('app:role_select')
    
    if role == 'parent':
        return register_parent(request)
    else:
        return register_tutor(request)

def register_educator(request):
    if request.method == 'POST':
        # Add your educator registration logic here
        # Create user and add to educator group
        # Redirect to login page on success
        return redirect('login')
    return render(request, 'app/register_educator.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Login attempt - Username: {username}")

        user = authenticate(username=username, password=password)
        print(f"Authentication result: {user}")

        if user is not None:
            login(request, user)
            print(f"Login successful for user: {user.username}")
            messages.success(request, 'Login successful!')
            
            # First check if user is a superuser
            if user.is_superuser:
                # Set admin role if not set
                if not user.user_role:
                    user.user_role = 'ADMIN'
                    user.user_id = 'ADM001'
                    user.user_phone_num = '1234567890'
                    user.profile_status = 'ACTIVE'
                    user.save()
                return redirect('app:admin_profile')
            
            # Check if this is the default staff user
            if user.username == 'staff1':
                # Set staff role if not set
                if not user.user_role:
                    user.user_role = 'STAFF'
                    user.user_id = 'STF001'
                    user.user_phone_num = '1234567890'
                    user.profile_status = 'ACTIVE'
                    user.save()
                return redirect('app:staff_profile')
            
            # Check user role and redirect accordingly
            if user.user_role == 'PARENT':
                return redirect('app:parent_profile')
            elif user.user_role == 'TUTOR':
                try:
                    tutor = Tutor.objects.get(user=user)
                    return redirect('app:tutor_profile')
                except Tutor.DoesNotExist:
                    messages.error(request, "Tutor profile not found.")
                    return redirect('app:login')
            elif user.user_role == 'STAFF':
                return redirect('app:staff_profile')
            elif user.user_role == 'ADMIN':
                return redirect('app:admin_profile')
            else:
                messages.error(request, 'Invalid user role.')
                return redirect('app:login')
        else:
            print("Login failed - invalid credentials")
            messages.error(request, 'Invalid username or password.')

    return render(request, 'app/login.html')

@login_required
def logout_view(request):
    """Handles logout for all user types with confirmation."""
    
    # Check user role and handle accordingly
    if hasattr(request.user, 'parent'):
        # Parent logout
        if request.method == 'POST' and 'yes' in request.POST:
            logout(request)
            messages.success(request, 'You have been logged out successfully.')
            return redirect('app:home')
        elif request.method == 'POST' and 'no' in request.POST:
            return redirect('app:parent_profile')
        return render(request, 'app/parent_logout.html')

    elif hasattr(request.user, 'tutor'):
        # Tutor logout
        if request.method == 'POST' and 'yes' in request.POST:
            logout(request)
            messages.success(request, 'You have been logged out successfully.')
            return redirect('app:home')
        elif request.method == 'POST' and 'no' in request.POST:
            return redirect('app:tutor_profile')
        return render(request, 'app/tutor_logout.html')

    elif request.user.user_role == 'STAFF':
        # Staff logout
        if request.method == 'POST' and 'yes' in request.POST:
            logout(request)
            messages.success(request, 'You have been logged out successfully.')
            return redirect('app:home')
        elif request.method == 'POST' and 'no' in request.POST:
            return redirect('app:staff_profile')
        return render(request, 'app/staff_logout.html')

    elif request.user.user_role == 'ADMIN':
        # Admin logout
        if request.method == 'POST' and 'yes' in request.POST:
            logout(request)
            messages.success(request, 'You have been logged out successfully.')
            return redirect('app:home')
        elif request.method == 'POST' and 'no' in request.POST:
            return redirect('app:admin_profile')
        return render(request, 'app/admin_logout.html')

    # If user role is not recognized, log them out immediately
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('app:home')  # Default to redirect to home if user role is invalid


@login_required
def parent_profile(request):
    try:
        parent = Parent.objects.get(user=request.user)
        return render(request, 'app/parent_profile.html', {'parent': parent})
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('app:login')

@login_required
def edit_parent_profile(request):
    try:
        parent = Parent.objects.get(user=request.user)
        if request.method == 'POST':
            # Get updated data
            # Update user fields
            parent.user.email = request.POST.get('email')
            parent.user.user_phone_num = request.POST.get('contact_number')

            # Update parent-specific fields
            parent.parent_name = request.POST.get('parent_name')
            parent.child_name = request.POST.get('child_name')
            parent.child_age = request.POST.get('child_age')
            parent.child_level = request.POST.get('child_level')
            
            
            # Save changes
            parent.user.save()
            parent.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('app:parent_profile')
            
        return render(request, 'app/edit_parent_profile.html', {'parent': parent})
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('app:login')

def index(request):
    """Home page view"""
    return render(request, 'app/index.html')

@login_required
def tutor_profile(request, pk=None):
    if pk:  # If a tutor ID is provided, fetch that tutor
        tutor = get_object_or_404(Tutor, user_id=pk)
    else:  # Otherwise, fetch the logged-in tutor's profile
        tutor = get_object_or_404(Tutor, user=request.user)

    return render(request, 'app/tutor_profile.html', {'tutor': tutor})

@login_required
def edit_tutor_profile(request):
    try:
        tutor = Tutor.objects.get(user=request.user)
        if request.method == 'POST':
            # Get updated data
            tutor_name = request.POST.get('tutor_name')
            print(f"Received tutor_name: {tutor_name}")  # Debug log
            
            if not tutor_name:
                messages.error(request, 'Tutor name is required.')
                return render(request, 'app/edit_tutor_profile.html', {'tutor': tutor})
            
            # Update tutor fields
            tutor.tutor_name = tutor_name
            tutor.education_level = request.POST.get('education_level', tutor.education_level)
            tutor.subject_taught = request.POST.get('subject_taught', tutor.subject_taught)
            
            # Update user fields
            user = tutor.user
            user.email = request.POST.get('email', user.email)
            user.user_phone_num = request.POST.get('contact_number', user.user_phone_num)
            
            # Handle certificate upload
            if 'certificate' in request.FILES:
                # Delete old certificate if it exists
                if tutor.certificate:
                    try:
                        tutor.certificate.delete(save=False)
                    except Exception as e:
                        print(f"Error deleting old certificate: {str(e)}")
                
                # Save new certificate
                tutor.certificate = request.FILES['certificate']
                print(f"New certificate uploaded: {tutor.certificate.name}")  # Debug log
            
            # Save changes
            try:
                user.save()
                tutor.save()
                print(f"Saved tutor with name: {tutor.tutor_name}")  # Debug log
                messages.success(request, 'Profile updated successfully!')
                return redirect('app:tutor_profile')
            except Exception as e:
                print(f"Error saving tutor: {str(e)}")  # Debug log
                messages.error(request, f'Error saving profile: {str(e)}')
                return render(request, 'app/edit_tutor_profile.html', {'tutor': tutor})
            
        return render(request, 'app/edit_tutor_profile.html', {'tutor': tutor})
    except Tutor.DoesNotExist:
        messages.error(request, "Tutor profile not found.")
        return redirect('app:login')


@login_required
def parent_search(request):
    tutors = Tutor.objects.all()  # Start with all tutors
    
    # Get filter criteria from GET request
    subject = request.GET.get('subject', '')
    tutor_level = request.GET.get('tutor_level', '')

    # Apply filters if parameters are selected
    if subject:
        tutors = tutors.filter(subject_taught__icontains=subject)
    
    if tutor_level:
        tutors = tutors.filter(education_level__icontains=tutor_level)

    # Retrieve session times for tutors
    tutor_sessions = []
    for tutor in tutors:
        # Retrieve the classes for this tutor
        classes = Class.objects.filter(tutor=tutor)  # Get classes for each tutor
        for class_obj in classes:
            # Format time slots for display
            formatted_slots = {}
            if class_obj.time_slots:
                for day, slots in class_obj.time_slots.items():
                    formatted_slots[day] = []
                    for slot in slots:
                        # Handle both string/integer and dictionary slot formats
                        if isinstance(slot, (str, int)):
                            hour = int(slot)
                            formatted_slots[day].append({
                                'hour': hour,
                                'display': f"{hour:02d}:00 - {(hour+1):02d}:00"
                            })
                        elif isinstance(slot, dict) and 'start_time' in slot:
                            start_hour = int(slot['start_time'].split(':')[0])
                            end_hour = int(slot['end_time'].split(':')[0])
                            formatted_slots[day].append({
                                'hour': start_hour,
                                'display': f"{start_hour:02d}:00 - {end_hour:02d}:00"
                            })
            
            tutor_sessions.append({
                'tutor': tutor, 
                'class': {
                    'class_id': class_obj.class_id,
                    'subject_name': class_obj.subject_name,
                    'description': class_obj.description,
                    'price': class_obj.price,
                    'student_level': class_obj.student_level,
                    'time_slots': formatted_slots
                }
            })

    context = {
        'tutors': tutors,
        'tutor_sessions': tutor_sessions,
        'selected_subject': subject,
        'selected_tutor_level': tutor_level
    }

    return render(request, 'app/parent_search.html', context)

@login_required
def parent_view_tutor_profile(request, pk):
    # Get the tutor based on the ID (pk)
    tutor = get_object_or_404(Tutor, user_id=pk)
    
    # You can choose not to display the edit buttons and handle the data as read-only.
    return render(request, 'app/parent_view_tutor_profile.html', {'tutor': tutor})

# ... existing code ...

@login_required
def parent_booking(request):
    try:
        parent = Parent.objects.get(user=request.user)
        favorite_tutors = parent.favorite_tutors_list.all()

        if request.method == "POST":
            selected_tutor_and_slot = request.POST.get('selected_tutor_and_slot')

            if not selected_tutor_and_slot:
                messages.error(request, "Please select a tutor and time slot!")
                return redirect('app:parent_booking')

            try:
                # Split the data
                tutor_id, class_id, start_time, end_time = selected_tutor_and_slot.split('|')

                # Get the related objects
                tutor_user = User.objects.get(id=tutor_id)
                tutor = Tutor.objects.get(user=tutor_user)
                selected_class = Class.objects.get(class_id=class_id)

                # Create schedule with weekday
                schedule = Schedule.objects.create(
                    name=f"Session with {parent.parent_name}",
                    subject=selected_class.subject_name,
                    price=selected_class.price,
                    tutor=tutor,
                    parent=parent,
                    capacity=1,
                    time_slots=[{
                        'weekday': timezone.now().strftime('%A'),
                        'start_time': start_time.replace(':00', ''),  # Remove seconds if present
                        'end_time': end_time.replace(':00', '')  # Remove seconds if present
                    }]
                )

                # Create booking
                booking = Booking.objects.create(
                    parent=parent,
                    tutor=tutor,
                    schedule=schedule,
                    subject_name=selected_class.subject_name,
                    session_time=timezone.now(),
                    booking_status="PENDING"
                )

                # Find and remove the favorite tutor entry
                favorite_to_remove = FavoriteTutor.objects.get(
                    parent=parent,
                    tutor=tutor,
                    selected_class=selected_class,
                    start_time=start_time,
                    end_time=end_time
                )
                favorite_to_remove.delete()

                messages.success(request, f"Booking request sent to {tutor.tutor_name}!")
                return redirect('app:parent_booking')

            except ValueError as e:
                messages.error(request, "Invalid booking data format!")
            except (User.DoesNotExist, Tutor.DoesNotExist, Class.DoesNotExist) as e:
                messages.error(request, "Selected tutor or class not found!")
            except FavoriteTutor.DoesNotExist as e:
                messages.error(request, "Selected favorite tutor not found!")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return render(request, 'app/parent_booking.html', {
            'favorite_tutors': favorite_tutors
        })

    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('app:parent_profile')

@login_required
def delete_favorite_tutor(request, favorite_id):
    if request.method == "POST":
        try:
            # Get the favorite tutor and verify it belongs to the current user
            favorite = FavoriteTutor.objects.get(
                id=favorite_id,
                parent__user=request.user
            )
            favorite.delete()
            messages.success(request, "Tutor removed from favorites successfully.")
        except FavoriteTutor.DoesNotExist:
            messages.error(request, "Favorite tutor not found.")
    return redirect('app:parent_search')


@login_required
def parent_payment(request):
    if not request.user.is_authenticated:
        return redirect('app:login')

    # Get all bookings for the parent
    bookings = Booking.objects.filter(
        parent=request.user.parent
    ).select_related(
        'tutor',
        'parent__user',
        'schedule'
    ).prefetch_related(
        'payment_set'
    ).order_by('-created_at')

    # Handle form submission for payment
    if request.method == 'POST':
        selected_bookings = request.POST.getlist('selected_bookings')
        print("Selected booking IDs:", selected_bookings)
        
        if not selected_bookings:
            messages.error(request, 'Please select at least one class to make payment')
            return redirect('app:parent_payment')
            
        # Verify selected bookings are valid for payment
        valid_bookings = []
        total_amount = 0
        
        for booking_id in selected_bookings:
            booking = bookings.filter(booking_id=booking_id).first()
            if booking:
                # A booking is valid if:
                # 1. It is CONFIRMED
                # 2. It has no completed payment
                payment = booking.payment_set.filter(payment_status='COMPLETED').first()
                
                if booking.booking_status == 'CONFIRMED' and not payment:
                    valid_bookings.append(booking_id)
                    total_amount += booking.schedule.price
        
        if valid_bookings:
            # Store booking IDs and total amount in session
            request.session['selected_booking_ids'] = valid_bookings
            request.session['total_amount'] = float(total_amount)
            return redirect('app:parent_payment_details')
        else:
            messages.error(request, 'Please select only confirmed and unpaid classes for payment')
            return redirect('app:parent_payment')

    context = {
        'bookings': bookings,
        'title': 'Payment'
    }
    return render(request, 'app/parent_payment.html', context)

@login_required
def parent_payment_details(request):
    """View for handling parent payment details page."""
    if not hasattr(request.user, 'parent'):
        messages.error(request, 'Access denied. You must be logged in as a parent.')
        return redirect('app:home')
    
    try:
        parent = request.user.parent
        
        # Get selected booking IDs from session
        selected_booking_ids = request.session.get('selected_booking_ids', [])
        total_amount = request.session.get('total_amount', 0)
        
        if not selected_booking_ids:
            messages.error(request, 'No classes selected for payment')
            return redirect('app:parent_payment')
        
        # Get selected bookings
        bookings = (
            Booking.objects.select_related('tutor', 'schedule')
            .filter(booking_id__in=selected_booking_ids)
        )
        
        if not bookings:
            messages.error(request, 'Selected bookings not found')
            return redirect('app:parent_payment')

        if request.method == "POST":
            payment_method = request.POST.get('paymentMethod')
            if not payment_method:
                messages.error(request, 'Please select a payment method')
                return redirect('app:parent_payment_details')

            try:
                # Update existing payment records for each booking
                for booking in bookings:
                    # Find existing pending payment
                    payment = Payment.objects.filter(
                        booking=booking,
                        payment_status='PENDING'
                    ).first()
                    
                    if payment:
                        # Update existing payment
                        payment.payment_status = 'COMPLETED'
                        payment.payment_method = payment_method
                        payment.save()
                    else:
                        # Create new payment only if no pending payment exists
                        Payment.objects.create(
                            parent=parent,
                            tutor=booking.tutor,
                            amount=booking.schedule.price,
                            payment_status='COMPLETED',
                            payment_method=payment_method,
                            booking=booking
                        )
                
                # Clear session data
                if 'selected_booking_ids' in request.session:
                    del request.session['selected_booking_ids']
                if 'total_amount' in request.session:
                    del request.session['total_amount']
                
                messages.success(request, 'Payment completed successfully!')
                return redirect('app:parent_payment')
                
            except Exception as e:
                messages.error(request, f'Error processing payment: {str(e)}')
                return redirect('app:parent_payment_details')

        # If GET request, show the payment details page
        context = {
            'bookings': bookings,
            'total_amount': total_amount,
            'title': 'Payment Details'
        }
        return render(request, 'app/parent_payment_details.html', context)
            
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('app:parent_payment')

@login_required
def parent_schedule(request):
    try:
        parent = Parent.objects.get(user=request.user)
        bookings = Booking.objects.filter(parent=parent).select_related(
            'tutor__user', 'schedule'
        ).order_by('session_time')

        # Get all payments for these bookings
        payments = Payment.objects.filter(booking__in=bookings).values('booking_id', 'payment_status')
        payment_dict = {p['booking_id']: p['payment_status'] for p in payments}

        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule_by_day = {day: [] for day in weekdays}

        for booking in bookings:
            if booking.schedule and booking.schedule.time_slots:
                for slot in booking.schedule.time_slots:
                    if isinstance(slot, str):
                        slot = json.loads(slot)
                    
                    weekday = slot.get('weekday', '')
                    if weekday in weekdays:
                        class_info = {
                            'booking_id': booking.booking_id,
                            'subject': booking.schedule.subject,
                            'tutor_name': booking.tutor.tutor_name,
                            'tutor_id': booking.tutor.user.id,
                            'start_time': slot.get('start_time', ''),
                            'end_time': slot.get('end_time', ''),
                            'status': booking.booking_status,
                            'payment_status': payment_dict.get(booking.booking_id)
                        }
                        schedule_by_day[weekday].append(class_info)

        context = {
            'weekdays': weekdays,
            'schedule_by_day': schedule_by_day
        }

        return render(request, 'app/parent_schedule.html', context)

    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('app:parent_profile')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('app:parent_profile')

@login_required
def parent_feedback(request):
    if request.method == 'POST':
        try:
            tutor_id = request.POST.get('tutor')
            schedule_id = request.POST.get('schedule_id')
            comments = request.POST.get('comments')
            flagged = request.POST.get('flagged') == 'on'

            if not all([tutor_id, schedule_id, comments]):
                messages.error(request, "Please fill in all required fields.")
                return redirect('app:parent_feedback')

            # Get the parent and tutor
            parent = Parent.objects.get(user=request.user)
            tutor = Tutor.objects.get(user_id=tutor_id)

            # Get the schedule
            try:
                schedule = Schedule.objects.get(schedule_id=schedule_id)
                
                # Check if this is a confirmed booking with payment
                booking = Booking.objects.filter(
                    parent=parent,
                    tutor=tutor,
                    schedule=schedule,
                    booking_status='CONFIRMED'
                ).first()

                if not booking:
                    messages.error(request, "Invalid session selection. Session must be confirmed.")
                    return redirect('app:parent_feedback')

                # Check payment status
                payment = Payment.objects.filter(booking=booking).order_by('-created_at').first()
                if not payment or payment.payment_status != 'COMPLETED':
                    messages.error(request, "Invalid session selection. Session must be paid.")
                    return redirect('app:parent_feedback')

                # Get time slot
                time_slots = schedule.time_slots
                if not time_slots or not isinstance(time_slots, list) or len(time_slots) == 0:
                    messages.error(request, "Invalid session time slots.")
                    return redirect('app:parent_feedback')
                
                time_slot = time_slots[0] if isinstance(time_slots, list) else time_slots

                # Check if feedback already exists
                existing_feedback = Feedback.objects.filter(
                    parent=parent,
                    tutor=tutor,
                    subject_name=schedule.subject,
                    comments__contains=time_slot  # Store time slot in comments since session_time is not used
                ).exists()

                if existing_feedback:
                    messages.error(request, "You have already submitted feedback for this session.")
                    return redirect('app:parent_feedback')

                # Format the time slot nicely
                if isinstance(time_slot, dict):
                    formatted_time = time_slot  # Keep the dictionary format for better parsing
                else:
                    try:
                        # Try to parse as JSON if it's a string
                        formatted_time = json.loads(time_slot)
                    except (json.JSONDecodeError, TypeError):
                        formatted_time = str(time_slot)

                # Create feedback with formatted time slot
                feedback = Feedback(
                    parent=parent,
                    tutor=tutor,
                    subject_name=schedule.subject,
                    comments=comments,  # Store only the user's comments
                    session_time=booking.session_time,  # Store the session time separately
                    flagged=flagged
                )
                feedback.save()

                messages.success(request, 'Feedback submitted successfully!')
                return redirect('app:parent_feedback')
            except Schedule.DoesNotExist:
                messages.error(request, "Invalid session selection.")
                return redirect('app:parent_feedback')

        except Exception as e:
            messages.error(request, f'Error submitting feedback: {str(e)}')
            return redirect('app:parent_feedback')

    # GET request - show form
    try:
        parent = Parent.objects.get(user=request.user)

        # Get confirmed bookings with payments
        completed_payments = Payment.objects.filter(
            booking__parent=parent,
            payment_status='COMPLETED'
        ).select_related(
            'booking',
            'booking__tutor',
            'booking__schedule'
        )

        print(f"Found {completed_payments.count()} completed payments")
        
        # Group bookings by tutor and subject
        tutor_classes = {}
        
        for payment in completed_payments:
            booking = payment.booking
            print(f"\nProcessing booking {booking.booking_id}:")
            print(f"- Subject: {booking.subject_name}")
            print(f"- Tutor: {booking.tutor.tutor_name}")
            print(f"- Status: {booking.booking_status}")
            
            # Skip if booking is not confirmed
            if booking.booking_status != 'CONFIRMED':
                print(f"- Skipping: Not confirmed")
                continue

            # Skip if no schedule
            if not booking.schedule:
                print(f"- Skipping: No schedule")
                continue

            # Get time slots
            schedule = booking.schedule
            print(f"- Schedule ID: {schedule.schedule_id}")
            print(f"- Raw time_slots: {schedule.time_slots}")

            # Convert time slots to list if needed
            time_slots = []
            raw_slots = schedule.time_slots

            if isinstance(raw_slots, str):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(raw_slots)
                    if isinstance(parsed, list):
                        time_slots = parsed
                    elif isinstance(parsed, dict):
                        time_slots = list(parsed.values())
                    else:
                        time_slots = [raw_slots]
                except json.JSONDecodeError:
                    time_slots = [raw_slots]
            elif isinstance(raw_slots, dict):
                time_slots = list(raw_slots.values())
            elif isinstance(raw_slots, list):
                time_slots = raw_slots
            else:
                time_slots = [str(raw_slots)]

            # Skip if no valid time slots
            if not time_slots:
                print(f"- Skipping: No time slots found")
                continue

            print(f"- Processed time slots: {time_slots}")

            # Create key for tutor-subject grouping
            key = f"{booking.tutor.user.id}_{booking.subject_name}"
            print(f"- Using key: {key}")
            
            # Initialize tutor-subject group if needed
            if key not in tutor_classes:
                tutor_classes[key] = {
                    "tutor": booking.tutor,
                    "subject_name": booking.subject_name,
                    "sessions": []
                }
            
            # Add each time slot as a session
            for slot in time_slots:
                if isinstance(slot, dict):
                    # Format the time slot in a readable way
                    weekday = slot.get('weekday', '')
                    start_time = slot.get('start_time', '')
                    end_time = slot.get('end_time', '')
                    formatted_time = f"{weekday} {start_time}:00 - {end_time}:00"
                else:
                    formatted_time = str(slot)

                session_data = {
                    "schedule_id": schedule.schedule_id,
                    "session_time": formatted_time,
                    "raw_data": slot  # Keep the raw data for reference
                }
                print(f"- Adding session: {session_data}")
                tutor_classes[key]["sessions"].append(session_data)

        # Convert sessions to JSON for template
        for key in tutor_classes:
            sessions_json = json.dumps(tutor_classes[key]["sessions"])
            print(f"\nJSON for {key}:")
            print(f"- Original sessions: {tutor_classes[key]['sessions']}")
            print(f"- JSON encoded: {sessions_json}")
            tutor_classes[key]["sessions"] = sessions_json

        if not tutor_classes:
            messages.info(request, "You don't have any confirmed and completed sessions to provide feedback for.")

        # Get previous feedbacks
        previous_feedbacks = Feedback.objects.filter(
            parent=parent
        ).select_related('tutor').order_by('-session_time')

        return render(request, 'app/parent_feedback.html', {
            'tutor_classes': tutor_classes.values(),
            'previous_feedbacks': previous_feedbacks
        })
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('app:parent_profile')

@login_required
def parent_add_favorite(request):
    if request.method == "POST":
        # Get the selected time slot from the form
        selected_tutor_and_slot = request.POST.get('selected_time_slot')

        print("Selected Time Slot:", selected_tutor_and_slot)  # Debugging

        if not selected_tutor_and_slot:
            messages.error(request, "No tutor or time slot selected!")
            return redirect('app:parent_search')

        try:
            # Ensure the format is correct (tutor_id|class_id|start_time|end_time)
            if selected_tutor_and_slot.count('|') != 3:
                raise ValueError("Invalid format for tutor and slot")

            # Split the string into tutor_id, class_id, start_time, and end_time
            selected_tutor_id, selected_class_id, selected_start_time, selected_end_time = selected_tutor_and_slot.split('|')

            # Retrieve the parent and tutor objects
            parent = Parent.objects.get(user=request.user)
            tutor = Tutor.objects.get(user_id=selected_tutor_id)
            selected_class = Class.objects.get(class_id=selected_class_id)

           # Create and add the favorite tutor entry
            favorite_tutor = FavoriteTutor.objects.create(
                parent=parent,
                tutor=tutor,
                selected_class=selected_class,
                start_time=selected_start_time,
                end_time=selected_end_time,
                price=selected_class.price
            )

            messages.success(request, f"{tutor.tutor_name} has been added as your favorite tutor!")
        except Parent.DoesNotExist:
            messages.error(request, "Parent profile not found.")
        except Tutor.DoesNotExist:
            messages.error(request, "Tutor not found.")
        except Class.DoesNotExist:
            messages.error(request, "Class not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return redirect('app:parent_search')

@login_required
def report(request):
    if request.method == 'POST':
        try:
            issue_type = request.POST.get('issue_type')
            description = request.POST.get('description')
            screenshot = request.FILES.get('screenshot')
            
            if not issue_type or not description:
                messages.error(request, 'Please fill in all required fields')
                return redirect('app:report')
            
            # Create new report
            report = SupportAssistance.objects.create(
                user=request.user,
                query_details=f"Issue Type: {issue_type}\n\nDescription: {description}",
                status='PENDING'
            )
            
            if screenshot:
                report.screenshot = screenshot
                report.save()
            
            messages.success(request, 'Your report has been submitted successfully')
            return redirect('app:report')
            
        except Exception as e:
            messages.error(request, f'Error submitting report: {str(e)}')
            return redirect('app:report')
    
    # Get previous reports for this user, ordered by query_id in descending order
    previous_reports = SupportAssistance.objects.filter(user=request.user).order_by('-query_id')
    
    context = {
        'previous_reports': previous_reports
    }
    
    return render(request, 'app/report.html', context)

@login_required
def tutor_booking(request):
    try:
        tutor = Tutor.objects.get(user=request.user)
        # Get all pending bookings for this tutor with related data
        pending_bookings = Booking.objects.filter(
            tutor=tutor,
            booking_status='PENDING'
        ).select_related(
            'parent',
            'parent__user',
            'schedule'
        ).order_by('-created_at')

        if request.method == "POST":
            booking_id = request.POST.get('booking_id')
            action = request.POST.get('action')
            
            try:
                booking = Booking.objects.get(booking_id=booking_id, tutor=tutor)
                
                if action == 'accept':
                    booking.booking_status = 'CONFIRMED'
                    booking.save()
                    
                    # Create a payment record for the booking
                    Payment.objects.create(
                        parent=booking.parent,
                        tutor=booking.tutor,
                        amount=booking.schedule.price,
                        payment_status='PENDING',
                        booking=booking
                    )
                    
                    messages.success(request, f"Booking from {booking.parent.parent_name} has been accepted!")
                
                elif action == 'decline':
                    booking.booking_status = 'CANCELLED'
                    booking.save()
                    messages.info(request, f"Booking from {booking.parent.parent_name} has been declined.")
                
                return redirect('app:tutor_booking')
                
            except Booking.DoesNotExist:
                messages.error(request, "Booking not found.")
        
        return render(request, 'app/tutor_booking.html', {
            'pending_bookings': pending_bookings
        })
        
    except Tutor.DoesNotExist:
        messages.error(request, "Tutor profile not found.")
        return redirect('app:login')


@login_required
def tutor_payment(request):
    # Check if user is a tutor
    if not hasattr(request.user, 'tutor'):
        messages.error(request, "Access denied. You must be logged in as a tutor.")
        return redirect('app:login')
        
    try:
        tutor = request.user.tutor
        
        # Get filter parameters
        status = request.GET.get('status')
        sort = request.GET.get('sort', '-created_at')  # Default sort by newest first
        
        # Get all payments for this tutor
        payments = Payment.objects.select_related(
            'booking',
            'parent'
        ).filter(
            tutor=tutor
        )
        
        # Apply filters
        if status:
            payments = payments.filter(payment_status=status)
        
        # Apply sorting
        if sort == 'created_at':
            payments = payments.order_by('created_at')
        elif sort == '-created_at':
            payments = payments.order_by('-created_at')
        elif sort == 'amount':
            payments = payments.order_by('amount')
        elif sort == '-amount':
            payments = payments.order_by('-amount')
        
        # Calculate total earnings
        total_earnings = payments.filter(payment_status='COMPLETED').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Calculate monthly earnings
        current_month = timezone.now().month
        monthly_earnings = payments.filter(
            payment_status='COMPLETED',
            created_at__month=current_month
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        context = {
            'payments': payments,
            'total_earnings': total_earnings,
            'monthly_earnings': monthly_earnings,
            'current_status': status,
            'current_sort': sort,
            'title': 'Payment History'
        }
        
        return render(request, 'app/tutor_payment.html', context)
            
    except Exception as e:
        logger.error(f"Error in tutor_payment view: {str(e)}")
        messages.error(request, f"An error occurred while loading payment information. Please try again.")
        return redirect('app:tutor_profile')

@login_required
def tutor_schedule(request):
    try:
        tutor = request.user.tutor
        print(f"\n=== DEBUG: Tutor Schedule ===")
        print(f"Tutor: {tutor}")
        
        # Get all schedules for this tutor
        schedules = Schedule.objects.filter(tutor=tutor.user_id)
        print(f"\nFound {schedules.count()} schedules")
        
        # Initialize schedule
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule_by_day = {day: [] for day in weekdays}  # Initialize all days with empty lists
        
        # Process each schedule
        for schedule in schedules:
            print(f"\nProcessing schedule {schedule.schedule_id}:")
            print(f"Subject: {schedule.subject}")
            
            if schedule.time_slots:
                print(f"Time slots: {schedule.time_slots}")
                
                # Parse time slots
                slots = schedule.time_slots
                if isinstance(slots, str):
                    import json
                    try:
                        slots = json.loads(slots)
                        print("Successfully parsed time slots JSON")
                    except json.JSONDecodeError:
                        print(f"Error parsing time slots: {e}")
                        continue
                
                # Ensure slots is a list
                if not isinstance(slots, list):
                    slots = [slots]
                
                # Add to schedule
                for slot in slots:
                    start_time = slot.get('start_time', '').replace('"', '')
                    print(f"Processing time slot: {start_time}")
                    
                    if start_time:
                        try:
                            # Extract hour from the time string
                            hour = int(start_time)
                            
                            # Convert to 12-hour format
                            formatted_time = f"{hour if hour <= 12 else hour-12}:00 {'AM' if hour < 12 else 'PM'}"
                            end_time = f"{(hour+1) if (hour+1) <= 12 else (hour+1)-12}:00 {'AM' if (hour+1) < 12 else 'PM'}"
                            
                            # Determine weekday based on time slot
                            weekday = None
                            if 9 <= hour < 12:
                                weekday = 'Monday'  # Morning slots on Monday
                            elif 13 <= hour < 17:
                                weekday = 'Tuesday'  # Afternoon slots on Tuesday
                            elif 17 <= hour < 21:
                                weekday = 'Wednesday'  # Evening slots on Wednesday
                            
                            if weekday:
                                class_info = {
                                    'schedule_id': schedule.schedule_id,
                                    'subject_name': schedule.subject,
                                    'start_time': formatted_time,
                                    'end_time': end_time,
                                    'description': schedule.description,
                                    'capacity': schedule.capacity,
                                    'price': schedule.price
                                }
                                schedule_by_day[weekday].append(class_info)
                                print(f"Added to {weekday} schedule: {class_info}")
                        except (ValueError, TypeError) as e:
                            print(f"Error processing time: {e}")
                            continue
            else:
                print("No time slots found")
        
        # Print final schedule
        print("\nFinal schedule:")
        for day in weekdays:
            classes = schedule_by_day[day]
            print(f"{day}: {len(classes)} classes")
            for class_info in classes:
                print(f"- {class_info['subject_name']} at {class_info['start_time']}")
        
        context = {
            'schedule_by_day': schedule_by_day,
            'weekdays': weekdays,
            'tutor': tutor
        }
        
        return render(request, 'app/tutor_schedule.html', context)
        
    except Exception as e:
        print("\n=== ERROR in tutor_schedule ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        # Don't redirect, show the error in development
        if settings.DEBUG:
            raise e
        
        messages.error(request, f'Error loading schedule: {str(e)}')
        return render(request, 'app/tutor_schedule.html', {
            'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'schedule_by_day': {},
            'error': str(e)
        })

@login_required
def tutor_feedback(request):
    try:
        tutor = Tutor.objects.get(user=request.user)

        # Get feedback related to the tutor, excluding invalid ones
        feedbacks = Feedback.objects.filter(
            tutor=tutor,
            status__in=['VALID', 'RESOLVED']  # Only show VALID and RESOLVED feedback
        ).select_related('parent').order_by('-session_time')
        
        # Get related schedules for each feedback
        feedback_data = []
        for feedback in feedbacks:
            try:
                # Get the booking related to this feedback
                booking = Booking.objects.filter(
                    tutor=tutor,
                    parent=feedback.parent,
                    subject_name=feedback.subject_name,
                    booking_status='CONFIRMED'
                ).first()

                slot_time = None
                if booking and booking.schedule:
                    schedule = booking.schedule
                    time_slots = schedule.time_slots
                    
                    # Parse time slots if it's a string
                    if isinstance(time_slots, str):
                        try:
                            time_slots = json.loads(time_slots)
                        except json.JSONDecodeError:
                            time_slots = []

                    # Get the first time slot
                    if time_slots:
                        if isinstance(time_slots, list) and len(time_slots) > 0:
                            slot = time_slots[0]
                        else:
                            slot = time_slots

                        if isinstance(slot, dict):
                            weekday = slot.get('weekday', '')
                            start_time = slot.get('start_time', '')
                            end_time = slot.get('end_time', '')
                            if weekday and start_time and end_time:
                                slot_time = f"{weekday} {start_time}:00 - {end_time}:00"
                        else:
                            try:
                                hour = int(slot)
                                slot_time = f"Monday {hour}:00 - {hour+1}:00"
                            except (ValueError, TypeError):
                                slot_time = None

                feedback_data.append({
                    'feedback': feedback,
                    'slot_time': slot_time,
                    'comments': feedback.comments.split('\n')[-1] if 'Time Slot:' in feedback.comments else feedback.comments
                })
            except Exception as e:
                print(f"Error processing feedback {feedback.feedback_id}: {e}")
                feedback_data.append({
                    'feedback': feedback,
                    'slot_time': None,
                    'comments': feedback.comments.split('\n')[-1] if 'Time Slot:' in feedback.comments else feedback.comments
                })
        
        return render(request, 'app/tutor_feedback.html', {
            'feedback_data': feedback_data,
            'status_colors': {
                'VALID': 'success',
                'RESOLVED': 'info'
            }
        })
    except Tutor.DoesNotExist:
        messages.error(request, "Tutor profile not found.")
        return redirect('app:tutor_profile')

def tutor_create_class(request):
    time_slots = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}

    if request.method == 'POST':
        # Get form data
        description = request.POST.get('description')
        price = request.POST.get('price')
        level = request.POST.get('level')

        # Initialize time_slots based on the selected days and hours
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days:
            slots = request.POST.getlist(f'time_slots_{day.lower()}')  # This retrieves the selected hours
            for slot in slots:
                # Convert the slot to start_time and end_time
                start_time = slot  # Assuming 'slot' contains the time in 'HH:mm' format
                end_time = str(int(slot[:2]) + 1) + slot[2:]  # Add 1 hour to the start time for end time
                time_slots[day].append({"start_time": start_time, "end_time": end_time})

        # Debug: Print form data to ensure it is received properly
        print("Form Data Received:")
        print(f"Description: {description}")
        print(f"Price: {price}")
        print(f"Level: {level}")
        print(f"Time Slots: {time_slots}")

        try:
            tutor = Tutor.objects.get(user=request.user)
            print(f"Tutor found: {tutor.tutor_name}")  # Ensure tutor is found

            # Set the subject name to the tutor's subject_taught
            subject_name = tutor.subject_taught  # Automatically set subject to tutor's subject_taught

            # Create the class
            new_class = Class.objects.create(
                tutor=tutor,
                subject_name=subject_name,  # Using tutor's subject_taught as subject_name
                description=description,
                time_slots={day.capitalize(): slots for day, slots in time_slots.items()},  # Store days with time slots
                price=price,
                student_level=level,
                session_time=None,  # Assuming no session time is selected
                capacity=1  # Fixed capacity of 1 student per slot
            )
            print(f"New class created: {new_class}")  # Check if the class was created successfully
            messages.success(request, 'Class created successfully!')
            return redirect('app:tutor_view_classes')  # Redirect to view classes page
        except Exception as e:
            print(f"Error creating class: {str(e)}")  # Capture any errors
            messages.error(request, f"Error creating class: {str(e)}")
            return redirect('app:tutor_create_class')

    try:
        tutor = Tutor.objects.get(user=request.user)
        context = {
            'tutor': tutor,
            'hours': range(24),  # Hours from 0 to 23
            'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'time_slots': time_slots, 
        }
        return render(request, 'app/tutor_create_class.html', context)
    except Tutor.DoesNotExist:
        messages.error(request, 'Tutor profile not found')
        return redirect('app:home')

@login_required
def tutor_update_class(request, class_id):
    try:
        # Get the class instance from the Class model
        class_instance = get_object_or_404(Class, class_id=class_id)

        # Ensure the tutor owns this class
        if class_instance.tutor.user != request.user:
            messages.error(request, 'You do not have permission to edit this class')
            return redirect('app:tutor_view_classes')

        if request.method == 'POST':
            # Update class data
            class_instance.description = request.POST.get('description')
            class_instance.price = request.POST.get('price')
            class_instance.student_level = request.POST.get('level')

            # Get time slots for each day
            time_slots = {}
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in days:
                # Retrieve the selected slots for each day
                slots = request.POST.getlist(f'time_slots_{day.lower()}')
                if slots:  # Only add days that have selected time slots
                    time_slots[day] = slots

            # Save the updated time slots to the class instance
            class_instance.time_slots = time_slots
            class_instance.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('app:tutor_view_classes')

        # For GET request, prepare time slots for display
        time_slots = class_instance.time_slots or {}
        context = {
            'class': class_instance,
            'tutor': class_instance.tutor,
            'hours': range(24),  # Hours from 0 to 23
            'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'time_slots': time_slots
        }
        return render(request, 'app/tutor_create_class.html', context)

    except Exception as e:
        messages.error(request, f'Error updating class: {str(e)}')
        return redirect('app:tutor_view_classes')

@login_required
def tutor_view_classes(request):
    try:
        tutor = Tutor.objects.get(user=request.user)
        classes = Class.objects.filter(tutor=tutor).order_by('-class_id')
        
        # Format time slots for each class
        for class_obj in classes:
            formatted_slots = {}
            for day, slots in class_obj.time_slots.items():
                formatted_slots[day] = []
                for slot in slots:
                    # Handle the case where slot is a number (legacy data)
                    if isinstance(slot, (int, str)):
                        hour = int(slot)
                        formatted_slots[day].append({
                            'hour': hour,
                            'display': f"{hour if hour <= 12 else hour-12}:00 {'AM' if hour < 12 else 'PM'}"
                        })
                    # Handle the case where slot is a dict with start_time and end_time
                    elif isinstance(slot, dict) and 'start_time' in slot:
                        start_hour = int(slot['start_time'].split(':')[0])
                        end_hour = int(slot['end_time'].split(':')[0])
                        formatted_slots[day].append({
                            'hour': start_hour,
                            'display': f"{start_hour:02d}:00 - {end_hour:02d}:00"
                        })
            class_obj.time_slots = formatted_slots
        
        context = {
            'tutor': tutor,
            'classes': classes,
        }
        return render(request, 'app/tutor_view_classes.html', context)
    except Tutor.DoesNotExist:
        messages.error(request, 'Tutor profile not found')
        return redirect('app:home')

@login_required
def tutor_delete_class(request, class_id):
    try:
        # Get the class instance from the 'additem_classes' table
        class_instance = get_object_or_404(Class, class_id=class_id)
        
        # Ensure the tutor owns this class
        if class_instance.tutor.user != request.user:
            messages.error(request, 'You do not have permission to delete this class.')
            return redirect('app:tutor_view_classes')
        
        # Delete the class
        class_instance.delete()
        messages.success(request, 'Class has been successfully deleted.')
        print(f"Deleting class: {class_instance}")
        return redirect('app:tutor_view_classes')

    except Exception as e:
        messages.error(request, f'Error deleting class: {str(e)}')
        return redirect('app:tutor_view_classes')

# Staff views
@login_required
def staff_profile(request):
    if request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    context = {
        'title': 'Staff Profile',
    }
    return render(request, 'app/staff_profile.html', context)

@login_required
def staff_support(request):
    if request.user.user_role != 'STAFF' and request.user.user_role != 'ADMIN':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')

    try:
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        search = request.GET.get('search', '')

        # Get all support queries with related user data
        queries = SupportAssistance.objects.select_related('user').all()

        # Apply filters
        if status_filter:
            queries = queries.filter(status=status_filter)
        
        if search:
            queries = queries.filter(
                Q(query_id__icontains=search) |
                Q(user__email__icontains=search) |
                Q(query_details__icontains=search)
            )

        # Order by status (open first) and then by query_id
        queries = queries.order_by(
            Case(
                When(status='OPEN', then=0),
                When(status='IN_PROGRESS', then=1),
                When(status='RESOLVED', then=2),
                default=3,
                output_field=IntegerField(),
            ),
            '-query_id'
        )

        # Calculate statistics
        total_queries = queries.count()
        open_count = queries.filter(status='OPEN').count()
        in_progress_count = queries.filter(status='IN_PROGRESS').count()
        resolved_count = queries.filter(status='RESOLVED').count()

        context = {
            'queries': queries,
            'total_queries': total_queries,
            'open_count': open_count,
            'in_progress_count': in_progress_count,
            'resolved_count': resolved_count,
            'current_status': status_filter,
            'search_query': search,
        }

        return render(request, 'app/staff_support.html', context)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('app:staff_profile')

@login_required
def staff_data(request):
    if request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')

    # User Statistics
    total_parents = Parent.objects.count()
    total_tutors = Tutor.objects.count()
    pending_tutors = User.objects.filter(user_role='TUTOR', profile_status='PENDING').count()
    active_tutors = User.objects.filter(user_role='TUTOR', profile_status='ACTIVE').count()

    # Class Statistics
    total_classes = Class.objects.count()
    active_classes = Class.objects.filter(capacity__gt=0).count()

    # Booking Statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(booking_status='PENDING').count()
    confirmed_bookings = Booking.objects.filter(booking_status='CONFIRMED').count()
    cancelled_bookings = Booking.objects.filter(booking_status='CANCELLED').count()

    # Payment Statistics
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(payment_status='COMPLETED').count()
    pending_payments = Payment.objects.filter(payment_status='PENDING').count()
    failed_payments = Payment.objects.filter(payment_status='FAILED').count()
    total_revenue = Payment.objects.filter(payment_status='COMPLETED').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Support Statistics
    total_queries = SupportAssistance.objects.count()
    pending_queries = SupportAssistance.objects.filter(status='PENDING').count()
    in_progress_queries = SupportAssistance.objects.filter(status='IN_PROGRESS').count()
    resolved_queries = SupportAssistance.objects.filter(status='RESOLVED').count()

    context = {
        'title': 'Data Management',
        # User Stats
        'total_parents': total_parents,
        'total_tutors': total_tutors,
        'pending_tutors': pending_tutors,
        'active_tutors': active_tutors,
        # Class Stats
        'total_classes': total_classes,
        'active_classes': active_classes,
        # Booking Stats
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        # Payment Stats
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'total_revenue': total_revenue,
        # Support Stats
        'total_queries': total_queries,
        'pending_queries': pending_queries,
        'in_progress_queries': in_progress_queries,
        'resolved_queries': resolved_queries,
    }
    
    return render(request, 'app/staff_data.html', context)

@login_required
def staff_feedback(request):
    if request.user.user_role != 'STAFF' and request.user.user_role != 'ADMIN':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')

    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        action = request.POST.get('action')
        response = request.POST.get('response')
        notes = request.POST.get('notes')

        try:
            feedback = Feedback.objects.get(feedback_id=feedback_id)
            
            if action == 'validate':
                feedback.status = 'VALID'
            elif action == 'invalidate':
                feedback.status = 'INVALID'
            elif action == 'resolve':
                feedback.status = 'RESOLVED'
            
            feedback.staff_response = response
            feedback.staff_notes = notes
            feedback.reviewed_by = request.user
            feedback.save()

            # Send notification to the parent
            messages.success(request, 'Feedback updated successfully.')
            return redirect('app:staff_feedback')
        except Feedback.DoesNotExist:
            messages.error(request, 'Feedback not found.')
            return redirect('app:staff_feedback')

    # Get all feedback entries, with flagged ones first
    feedback_list = Feedback.objects.all().order_by('-flagged', '-created_at')
    
    context = {
        'title': 'Feedback Management',
        'feedback_list': feedback_list,
    }
    return render(request, 'app/staff_feedback.html', context)

@login_required
def staff_notification(request):
    if request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    from .models import Notification, UserNotification
    from additem.models import User
    
    def get_target_users(target_audience):
        """Get users based on target audience"""
        if target_audience == 'TUTORS':
            return User.objects.filter(user_role='TUTOR', is_active=True)
        elif target_audience == 'PARENTS':
            return User.objects.filter(user_role='PARENT', is_active=True)
        elif target_audience == 'ALL':
            return User.objects.filter(user_role__in=['TUTOR', 'PARENT'], is_active=True)
        return User.objects.none()
    
    def send_notification(notification):
        """Send notification to target users"""
        try:
            # Get target users based on audience
            target_users = get_target_users(notification.target_audience)
            
            # Create UserNotification for each target user
            UserNotification.objects.bulk_create([
                UserNotification(
                    user=user,
                    notification=notification,
                    is_read=False
                ) for user in target_users
            ])
            
            # If email delivery is selected, send emails
            if notification.delivery_method == 'EMAIL':
                for user in target_users:
                    try:
                        send_mail(
                            notification.title,
                            notification.content,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send email to {user.email}: {str(e)}")
            
            # Mark notification as sent
            notification.status = 'SENT'
            notification.sent_at = timezone.now()
            notification.save()
            
            return True
        except Exception as e:
            notification.status = 'FAILED'
            notification.save()
            logger.error(f"Failed to send notification {notification.id}: {str(e)}")
            return False

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        target_audience = request.POST.get('target_audience')
        delivery_method = request.POST.get('delivery_method')
        
        try:
            print(f"\nCreating notification:")
            print(f"Title: {title}")
            print(f"Content: {content}")
            print(f"Target Audience: {target_audience}")
            print(f"Delivery Method: {delivery_method}")
            
            # Validate inputs
            if not all([title, content, target_audience, delivery_method]):
                raise ValueError("All fields are required")
            
            if len(content) > 500:
                raise ValueError("Content must be less than 500 characters")
            
            # Create and send notification immediately
            notification = Notification.objects.create(
                title=title,
                content=content,
                target_audience=target_audience,
                delivery_method=delivery_method,
                created_by=request.user,
                scheduled_for=timezone.now(),  # Set to current time
                status='PENDING'
            )
            print(f"Created notification with ID: {notification.id}")
            
            # Get target users before sending
            target_users = get_target_users(target_audience)
            print(f"Found {target_users.count()} target users:")
            for user in target_users:
                print(f"- {user.username} ({user.user_role})")
            
            if send_notification(notification):
                messages.success(request, 'Notification sent successfully!')
            else:
                messages.error(request, 'Failed to send notification. Please try again.')
            
            return redirect('app:staff_notification')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating notification: {str(e)}')
    
    # Get all notifications with their delivery status
    notifications = Notification.objects.select_related('created_by').order_by('-created_at')
    
    # Calculate notification statistics
    stats = {
        'total': notifications.count(),
        'sent': notifications.filter(status='SENT').count(),
        'pending': notifications.filter(status='PENDING').count(),
        'failed': notifications.filter(status='FAILED').count()
    }
    
    return render(request, 'app/staff_notification.html', {
        'notifications': notifications,
        'target_choices': [
            ('TUTORS', 'All Tutors'),
            ('PARENTS', 'All Parents'),
            ('ALL', 'All Users')
        ],
        'delivery_methods': [
            ('IN_APP', 'In-App Notification'),
            ('EMAIL', 'Email')
        ],
        'stats': stats
    })

# Admin views
@login_required
def admin_profile(request):
    if request.user.user_role not in ['ADMIN', 'STAFF']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    try:
        # Get pending counts
        pending_users_count = User.objects.filter(profile_status='PENDING').count()
        pending_tutors_count = Tutor.objects.filter(user__profile_status='PENDING').count()
        pending_payments_count = Payment.objects.filter(payment_status='PENDING').count()

        context = {
            'admin': {
                'admin_name': request.user.username
            },
            'pending_users_count': pending_users_count,
            'pending_tutors_count': pending_tutors_count,
            'pending_payments_count': pending_payments_count,
            'year': datetime.now().year,
            'title': 'Admin Dashboard'
        }
        return render(request, 'app/admin_profile.html', context)
    except Exception as e:
        messages.error(request, f'Error loading admin profile: {str(e)}')
        return redirect('app:login')

@login_required
def admin_user_management(request):
    if request.user.user_role not in ['ADMIN', 'STAFF']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    try:
        # Handle status update form submission
        if request.method == 'POST':
            user_id = request.POST.get('user_id')
            new_status = request.POST.get('status')
            if user_id and new_status:
                try:
                    user = User.objects.get(id=user_id)
                    user.profile_status = new_status
                    user.save()
                    messages.success(request, f'Status updated successfully for {user.username}')
                except User.DoesNotExist:
                    messages.error(request, 'User not found')
                except Exception as e:
                    messages.error(request, f'Error updating status: {str(e)}')
            return redirect('app:admin_user_management')
        
        # Get filter parameters
        search_query = request.GET.get('search', '')
        role_filter = request.GET.get('role', '')
        status_filter = request.GET.get('status', '')
        
        # Start with all users
        users = User.objects.all()
        
        # Apply filters
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(user_phone_num__icontains=search_query)
            )
        
        if role_filter:
            users = users.filter(user_role=role_filter)
            
        if status_filter:
            users = users.filter(profile_status=status_filter)
        
        # Order by join date
        users = users.order_by('-date_joined')
        
        # Prepare choices for dropdowns
        role_choices = [
            ('PARENT', 'Parent'),
            ('TUTOR', 'Tutor'),
            ('ADMIN', 'Admin'),
            ('STAFF', 'Staff')
        ]
        
        status_choices = [
            ('ACTIVE', 'Active'),
            ('PENDING', 'Pending'),
            ('SUSPENDED', 'Suspended')
        ]
        
        context = {
            'users': users,
            'search_query': search_query,
            'role_filter': role_filter,
            'status_filter': status_filter,
            'role_choices': role_choices,
            'status_choices': status_choices,
            'title': 'User Management'
        }
        
        return render(request, 'app/admin_user_management.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading user management page: {str(e)}')
        return redirect('app:admin_profile')

@login_required
def admin_tutor_management(request):
    if request.user.user_role not in ['ADMIN', 'STAFF']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    try:
        # Get filter parameters
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        subject_filter = request.GET.get('subject', '')
        
        # Start with all tutors and prefetch related data
        tutors = Tutor.objects.select_related('user').prefetch_related(
            'class_set',  # Get tutor's classes
            'booking_set'  # Get tutor's bookings
        )
        
        # Apply filters
        if search_query:
            tutors = tutors.filter(
                Q(tutor_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(subject_taught__icontains=search_query)
            )
        if status_filter:
            tutors = tutors.filter(user__profile_status=status_filter.upper())
        if subject_filter:
            tutors = tutors.filter(subject_taught__icontains=subject_filter)
            
        # Get unique subjects for filter dropdown
        all_subjects = Tutor.objects.values_list('subject_taught', flat=True).distinct()
        
        # Get statistics
        total_tutors = tutors.count()
        active_tutors = tutors.filter(user__profile_status='ACTIVE').count()
        pending_tutors = tutors.filter(user__profile_status='PENDING').count()
        inactive_tutors = tutors.filter(user__profile_status='INACTIVE').count()
        
        # Calculate additional stats for each tutor
        for tutor in tutors:
            tutor.total_classes = tutor.class_set.count()
            tutor.total_bookings = tutor.booking_set.count()
            tutor.active_bookings = tutor.booking_set.filter(booking_status='CONFIRMED').count()
        
        context = {
            'tutors': tutors,
            'search_query': search_query,
            'status_filter': status_filter,
            'subject_filter': subject_filter,
            'all_subjects': all_subjects,
            'status_choices': User.PROFILE_STATUS,
            'stats': {
                'total': total_tutors,
                'active': active_tutors,
                'pending': pending_tutors,
                'inactive': inactive_tutors
            }
        }
        return render(request, 'app/admin_tutor_management.html', context)
    except Exception as e:
        messages.error(request, f'Error loading tutor management page: {str(e)}')
        return redirect('app:admin_profile')

@login_required
def admin_payment_management(request):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    try:
        # Get filter parameters
        status = request.GET.get('status')
        date_filter = request.GET.get('date_filter', 'all')
        search = request.GET.get('search', '')

        # Base query
        payments = Payment.objects.select_related(
            'parent', 
            'tutor', 
            'booking'
        ).all()

        # Apply filters
        if status:
            payments = payments.filter(payment_status=status)
            
        if search:
            payments = payments.filter(
                Q(parent__parent_name__icontains=search) |
                Q(tutor__tutor_name__icontains=search) |
                Q(payment_id__icontains=search)
            )
            
        # Apply date filter
        today = timezone.now()
        if date_filter == 'today':
            payments = payments.filter(created_at__date=today.date())
        elif date_filter == 'week':
            week_ago = today - timezone.timedelta(days=7)
            payments = payments.filter(created_at__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timezone.timedelta(days=30)
            payments = payments.filter(created_at__gte=month_ago)

        # Calculate statistics
        total_revenue = payments.filter(payment_status='COMPLETED').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        completed_count = payments.filter(payment_status='COMPLETED').count()
        pending_count = payments.filter(payment_status='PENDING').count()
        failed_count = payments.filter(payment_status='FAILED').count()
        
        # Get recent payments
        recent_payments = payments.order_by('-created_at')[:10]

        context = {
            'payments': payments,
            'recent_payments': recent_payments,
            'total_revenue': total_revenue,
            'completed_payments': completed_count,
            'pending_payments': pending_count,
            'failed_payments': failed_count,
            'current_status': status,
            'current_date_filter': date_filter,
            'search_query': search
        }
        
        return render(request, 'app/admin_payment_management.html', context)
            
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('app:admin_profile')

@login_required
def admin_administration(request):
    if request.user.user_role not in ['ADMIN', 'STAFF']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    try:
        # System Information
        system_info = {
            'django_version': django.get_version(),
            'python_version': platform.python_version(),
            'os_info': platform.platform(),
            'timezone': settings.TIME_ZONE,
        }
        
        # User Statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_parents = Parent.objects.select_related('user').count()
        total_tutors = Tutor.objects.select_related('user').count()
        active_tutors = Tutor.objects.select_related('user').filter(user__profile_status='ACTIVE').count()
        pending_tutors = Tutor.objects.select_related('user').filter(user__profile_status='PENDING').count()
        
        # Booking and Payment Statistics
        total_bookings = Booking.objects.count()
        recent_bookings = (Booking.objects.select_related('parent__user', 'tutor__user', 'schedule')
                         .order_by('-session_time')[:5])
        
        # Convert time_slots from string to dict if needed
        for booking in recent_bookings:
            if booking.schedule and booking.schedule.time_slots:
                if isinstance(booking.schedule.time_slots, str):
                    try:
                        booking.schedule.time_slots = json.loads(booking.schedule.time_slots)
                    except json.JSONDecodeError:
                        booking.schedule.time_slots = None
        
        total_payments = Payment.objects.count()
        completed_payments = Payment.objects.filter(payment_status='COMPLETED').count()
        pending_payments = Payment.objects.filter(payment_status='PENDING').count()
        
        # Recent Activities
        recent_users = User.objects.order_by('-date_joined')[:5]
        recent_payments = Payment.objects.select_related('parent__user', 'tutor__user').order_by('-payment_id')[:5]
        
        # Parent Statistics
        parents_with_bookings = Parent.objects.filter(booking__isnull=False).distinct().count()
        parents_with_payments = Parent.objects.filter(payment__isnull=False).distinct().count()
        
        # Tutor Statistics
        tutors_with_classes = Tutor.objects.filter(class__isnull=False).distinct().count()
        tutors_with_bookings = Tutor.objects.filter(booking__isnull=False).distinct().count()
        
        context = {
            'system_info': system_info,
            # User Stats
            'total_users': total_users,
            'active_users': active_users,
            'total_parents': total_parents,
            'total_tutors': total_tutors,
            'active_tutors': active_tutors,
            'pending_tutors': pending_tutors,
            # Booking and Payment Stats
            'total_bookings': total_bookings,
            'recent_bookings': recent_bookings,
            'total_payments': total_payments,
            'completed_payments': completed_payments,
            'pending_payments': pending_payments,
            # Recent Activities
            'recent_users': recent_users,
            'recent_payments': recent_payments,
            # Parent Stats
            'parents_with_bookings': parents_with_bookings,
            'parents_with_payments': parents_with_payments,
            # Tutor Stats
            'tutors_with_classes': tutors_with_classes,
            'tutors_with_bookings': tutors_with_bookings,
        }
        
        return render(request, 'app/admin_administration.html', context)
    except Exception as e:
        messages.error(request, f'Error loading administration page: {str(e)}')
        return redirect('app:admin_profile')

@login_required
def tutor_approve(request, tutor_id):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    tutor.user.profile_status = 'ACTIVE'
    tutor.user.save()
    messages.success(request, f'Tutor {tutor.tutor_name} has been approved.')
    return redirect('app:tutor_details', tutor_id=tutor_id)

@login_required
def tutor_decline(request, tutor_id):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    tutor.user.profile_status = 'INACTIVE'
    tutor.user.save()
    messages.success(request, f'Tutor {tutor.tutor_name} has been declined.')
    return redirect('app:tutor_details', tutor_id=tutor_id)

@login_required
def admin_export_tutors(request):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    # Add export logic here if needed
    return redirect('app:admin_tutor_management')

@login_required
def admin_export_payments(request):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    # Add export logic here if needed
    return redirect('app:admin_payment_management')

@login_required
def tutor_details(request, tutor_id):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        verification_notes = request.POST.get('verification_notes')
        try:
            tutor.user.profile_status = new_status
            tutor.user.save()  # Save the user object
            tutor.verification_notes = verification_notes
            tutor.save()  # Save the tutor object
            messages.success(request, 'Tutor status updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating tutor status: {str(e)}')
        return redirect('app:tutor_details', tutor_id=tutor_id)
    context = {
        'tutor': tutor,
    }
    return render(request, 'app/admin_tutor_details.html', context)

@login_required
def admin_generate_payment_report(request):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    # Add report generation logic here if needed
    return redirect('app:admin_payment_management')

@login_required
def tutor_approve(request, tutor_id):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    tutor.user.profile_status = 'ACTIVE'
    tutor.user.save()
    messages.success(request, f'Tutor {tutor.tutor_name} has been approved.')
    return redirect('app:tutor_details', tutor_id=tutor_id)

@login_required
def tutor_decline(request, tutor_id):
    if request.user.user_role != 'ADMIN' and request.user.user_role != 'STAFF':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')
    
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    tutor.user.profile_status = 'INACTIVE'
    tutor.user.save()
    messages.success(request, f'Tutor {tutor.tutor_name} has been declined.')
    return redirect('app:tutor_details', tutor_id=tutor_id)

@login_required
def admin_delete_user(request, user_id):
    if request.user.user_role != 'ADMIN':
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('app:admin_user_management')
    
    if request.method == 'POST':
        try:
            user_to_delete = User.objects.get(id=user_id)
            
            # Don't allow deleting your own account
            if user_to_delete == request.user:
                messages.error(request, 'You cannot delete your own account.')
                return redirect('app:admin_user_management')
            
            # Delete associated profile based on user role
            if user_to_delete.user_role == 'PARENT':
                Parent.objects.filter(user=user_to_delete).delete()
            elif user_to_delete.user_role == 'TUTOR':
                Tutor.objects.filter(user=user_to_delete).delete()
            elif user_to_delete.user_role == 'STAFF':
                Staff.objects.filter(user=user_to_delete).delete()
            
            # Delete the user
            username = user_to_delete.username
            user_to_delete.delete()
            
            messages.success(request, f'User {username} has been deleted successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
    
    return redirect('app:admin_user_management')

@login_required
def tutor_student(request):
    try:
        tutor = request.user.tutor
        
        # Get filter parameters
        subject = request.GET.get('subject', '')
        level = request.GET.get('level', '')
        
        # Get confirmed bookings for this tutor
        students = Booking.objects.filter(
            tutor=tutor,
            booking_status='CONFIRMED'
        ).select_related(
            'parent',
            'parent__user'
        ).order_by('-created_at')
        
        # Apply filters if provided
        if subject:
            students = students.filter(subject_name=subject)
        if level:
            students = students.filter(parent__child_level=level)
        
        # Get unique subjects and levels for filters
        subjects = Booking.objects.filter(
            tutor=tutor,
            booking_status='CONFIRMED'
        ).values_list('subject_name', flat=True).distinct()
        
        levels = Parent.objects.filter(
            booking__tutor=tutor,
            booking__booking_status='CONFIRMED'
        ).values_list('child_level', flat=True).distinct()
        
        context = {
            'students': students,
            'subjects': subjects,
            'levels': levels,
            'selected_subject': subject,
            'selected_level': level
        }
        
        return render(request, 'app/tutor_student.html', context)
        
    except Exception as e:
        print(f"Error in tutor_student: {str(e)}")
        messages.error(request, 'Error loading student list')
        return render(request, 'app/tutor_student.html', {
            'students': [],
            'subjects': [],
            'levels': []
        })

@login_required
def tutor_report(request):
    try:
        tutor = request.user.tutor
        
        # Get total students (unique parents from confirmed bookings)
        total_students = Parent.objects.filter(
            booking__tutor=tutor,
            booking__booking_status='CONFIRMED'
        ).distinct().count()
        
        # Get total active classes
        total_classes = Schedule.objects.filter(
            tutor=tutor
        ).count()
        
        # Get recent bookings
        recent_bookings = Booking.objects.filter(
            tutor=tutor
        ).order_by('-created_at')[:5]
        
        # Get recent valid/resolved feedback with time slots
        recent_feedback_data = []
        recent_feedbacks = Feedback.objects.filter(
            tutor=tutor,
            status__in=['VALID', 'RESOLVED']  # Only show VALID and RESOLVED feedback
        ).select_related('parent').order_by('-created_at')[:5]

        for feedback in recent_feedbacks:
            # Get the booking related to this feedback
            booking = Booking.objects.filter(
                tutor=tutor,
                parent=feedback.parent,
                subject_name=feedback.subject_name,
                booking_status='CONFIRMED'
            ).first()

            slot_time = None
            if booking and booking.schedule:
                schedule = booking.schedule
                time_slots = schedule.time_slots
                
                # Parse time slots if it's a string
                if isinstance(time_slots, str):
                    try:
                        time_slots = json.loads(time_slots)
                    except json.JSONDecodeError:
                        time_slots = []

                # Get the first time slot
                if time_slots:
                    if isinstance(time_slots, list) and len(time_slots) > 0:
                        slot = time_slots[0]
                    else:
                        slot = time_slots

                    if isinstance(slot, dict):
                        # Format the slot time
                        weekday = slot.get('weekday', '')
                        start_time = slot.get('start_time', '')
                        end_time = slot.get('end_time', '')
                        if weekday and start_time and end_time:
                            slot_time = f"{weekday} {start_time}:00 - {end_time}:00"
                    else:
                        # If slot is just a number (hour)
                        try:
                            hour = int(slot)
                            slot_time = f"Monday {hour}:00 - {hour+1}:00"
                        except (ValueError, TypeError):
                            pass

            # Clean up comments by removing time slot info
            comments = feedback.comments
            if comments:
                if "Time Slot:" in comments:
                    comments = comments.split("Time Slot:")[0].strip()

            recent_feedback_data.append({
                'feedback': feedback,
                'comments': comments,
                'slot_time': slot_time
            })
        
        # Calculate average rating (if you have a rating system)
        # For now, we'll set it to None
        average_rating = None
        
        context = {
            'total_students': total_students,
            'total_classes': total_classes,
            'recent_bookings': recent_bookings,
            'recent_feedback': recent_feedback_data,
            'average_rating': average_rating,
            'status_colors': {  # Add status colors for badges
                'VALID': 'success',
                'RESOLVED': 'info'
            }
        }
        
        return render(request, 'app/tutor_report.html', context)
        
    except Exception as e:
        print(f"Error in tutor_report: {str(e)}")
        messages.error(request, 'Error loading report')
        return render(request, 'app/tutor_report.html', {
            'total_students': 0,
            'total_classes': 0,
            'recent_bookings': [],
            'recent_feedback': [],
            'average_rating': None,
            'status_colors': {
                'VALID': 'success',
                'RESOLVED': 'info'
            }
        })

@login_required
def tutor_send_feedback(request, booking_id):
    if request.method == 'POST':
        try:
            booking = Booking.objects.get(
                booking_id=booking_id,
                tutor=request.user.tutor,
                booking_status='CONFIRMED'
            )
            
            feedback = Feedback.objects.create(
                parent=booking.parent,
                tutor=booking.tutor,
                subject_name=booking.subject_name,
                session_time=booking.session_time,
                comments=request.POST.get('feedback', ''),
                status='PENDING'
            )

            messages.success(request, 'Feedback sent successfully')
            
        except Booking.DoesNotExist:
            messages.error(request, "Invalid booking")
        except Exception as e:
            print(f"Error sending feedback: {str(e)}")
            messages.error(request, 'Error sending feedback')
    
    return redirect('app:tutor_student')

@login_required
def parent_payment_details(request):
    """View for handling parent payment details page."""
    if not hasattr(request.user, 'parent'):
        messages.error(request, 'Access denied. You must be logged in as a parent.')
        return redirect('app:home')
    
    try:
        parent = request.user.parent
        
        # Get selected booking IDs from session
        selected_booking_ids = request.session.get('selected_booking_ids', [])
        total_amount = request.session.get('total_amount', 0)
        
        if not selected_booking_ids:
            messages.error(request, 'No classes selected for payment')
            return redirect('app:parent_payment')
        
        # Get selected bookings
        bookings = (
            Booking.objects.select_related('tutor', 'schedule')
            .filter(booking_id__in=selected_booking_ids)
        )
        
        if not bookings:
            messages.error(request, 'Selected bookings not found')
            return redirect('app:parent_payment')

        if request.method == "POST":
            payment_method = request.POST.get('paymentMethod')
            if not payment_method:
                messages.error(request, 'Please select a payment method')
                return redirect('app:parent_payment_details')

            try:
                # Update existing payment records for each booking
                for booking in bookings:
                    # Find existing pending payment
                    payment = Payment.objects.filter(
                        booking=booking,
                        payment_status='PENDING'
                    ).first()
                    
                    if payment:
                        # Update existing payment
                        payment.payment_status = 'COMPLETED'
                        payment.payment_method = payment_method
                        payment.save()
                    else:
                        # Create new payment only if no pending payment exists
                        Payment.objects.create(
                            parent=parent,
                            tutor=booking.tutor,
                            amount=booking.schedule.price,
                            payment_status='COMPLETED',
                            payment_method=payment_method,
                            booking=booking
                        )
                
                # Clear session data
                if 'selected_booking_ids' in request.session:
                    del request.session['selected_booking_ids']
                if 'total_amount' in request.session:
                    del request.session['total_amount']
                
                messages.success(request, 'Payment completed successfully!')
                return redirect('app:parent_payment')
                
            except Exception as e:
                messages.error(request, f'Error processing payment: {str(e)}')
                return redirect('app:parent_payment_details')

        # If GET request, show the payment details page
        context = {
            'bookings': bookings,
            'total_amount': total_amount,
            'title': 'Payment Details'
        }
        return render(request, 'app/parent_payment_details.html', context)
            
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('app:parent_payment')

@login_required
@require_POST
def update_support_query_status(request, query_id):
    if request.user.user_role not in ['STAFF', 'ADMIN']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    try:
        # Try to get status from JSON data
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                status = data.get('status')
                print(f"Received JSON data: {data}")  # Debug log
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")  # Debug log
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        else:
            status = request.POST.get('status')
            print(f"Received POST data: {request.POST}")  # Debug log
        
        if not status:
            return JsonResponse({'error': 'Status is required'}, status=400)
            
        query = get_object_or_404(SupportAssistance, query_id=query_id)
        print(f"Found query: {query.query_id}, current status: {query.status}")  # Debug log
        
        query.status = status
        query.save()
        print(f"Updated query status to: {status}")  # Debug log
        
        return JsonResponse({'message': 'Status updated successfully'})
        
    except Exception as e:
        print(f"Error updating status: {str(e)}")  # Debug log
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def respond_to_support_query(request, query_id):
    if request.user.user_role not in ['STAFF', 'ADMIN']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    try:
        # Try to get response from JSON data
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                response = data.get('response')
                print(f"Received JSON data: {data}")  # Debug log
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")  # Debug log
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        else:
            response = request.POST.get('response')
            print(f"Received POST data: {request.POST}")  # Debug log
        
        if not response:
            return JsonResponse({'error': 'Response is required'}, status=400)
            
        query = get_object_or_404(SupportAssistance, query_id=query_id)
        print(f"Found query: {query.query_id}")  # Debug log
        
        query.response = response
        query.status = 'IN_PROGRESS'
        query.save()
        print(f"Updated query response and status")  # Debug log
        
        return JsonResponse({'message': 'Response sent successfully'})
        
    except Exception as e:
        print(f"Error sending response: {str(e)}")  # Debug log
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def respond_to_support_query(request, query_id):
    if request.method == 'POST' and request.user.user_role == 'STAFF':
        try:
            query = SupportAssistance.objects.get(query_id=query_id)
            response = request.POST.get('response')
            
            if not response:
                messages.error(request, 'Response is required.')
                return redirect('app:staff_support')
            
            # Update query with response
            query.response = response
            query.responded_by = request.user
            query.response_date = timezone.now()
            
            # If query is open, move it to in progress
            if query.status == 'OPEN':
                query.status = 'IN_PROGRESS'
            
            query.save()
            
            # Send notification to user
            Notification.objects.create(
                user=query.user,
                title='Response to Your Support Query',
                content=f'Your support query #{query_id} has received a response.',
                notification_type='SUPPORT',
                reference_id=query_id,
                target_audience='INDIVIDUAL',
                delivery_method='IN_APP',
                created_by=request.user,
                scheduled_for=timezone.now()
            )
            
            messages.success(request, 'Response sent successfully.')
            
        except SupportAssistance.DoesNotExist:
            messages.error(request, "Query not found.")
        except Exception as e:
            messages.error(request, f'Error sending response: {str(e)}')
    else:
        messages.error(request, 'Invalid request or insufficient permissions.')
    
    return redirect('app:staff_support')

@login_required
@require_POST
def update_support_query_status(request, query_id):
    if request.user.user_role not in ['STAFF', 'ADMIN']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    try:
        # Try to get status from JSON data
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                status = data.get('status')
                print(f"Received JSON data: {data}")  # Debug log
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")  # Debug log
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        else:
            status = request.POST.get('status')
            print(f"Received POST data: {request.POST}")  # Debug log
        
        if not status:
            return JsonResponse({'error': 'Status is required'}, status=400)
            
        query = get_object_or_404(SupportAssistance, query_id=query_id)
        print(f"Found query: {query.query_id}, current status: {query.status}")  # Debug log
        
        query.status = status
        query.save()
        print(f"Updated query status to: {status}")  # Debug log
        
        return JsonResponse({'message': 'Status updated successfully'})
        
    except Exception as e:
        print(f"Error updating status: {str(e)}")  # Debug log
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def chat_inbox(request):
    """View for displaying chat inbox with list of conversations"""
    user = request.user
    
    # Get all unique chat partners based on user role
    if user.user_role == 'PARENT':
        parent_id = user.id
        # Get all tutors this parent has chatted with
        chat_users = User.objects.filter(
            user_role='TUTOR',
            id__in=Communication.objects.filter(parent_id=parent_id).values_list('tutor_id', flat=True).distinct()
        )
    else:  # TUTOR
        tutor_id = user.id
        # Get all parents this tutor has chatted with
        chat_users = User.objects.filter(
            user_role='PARENT',
            id__in=Communication.objects.filter(tutor_id=tutor_id).values_list('parent_id', flat=True).distinct()
        )
    
    # Get latest message for each chat
    conversations = []
    for chat_user in chat_users:
        if user.user_role == 'PARENT':
            latest_message = Communication.objects.filter(
                parent_id=user.id,
                tutor_id=chat_user.id
            ).order_by('-chat_id').first()
        else:
            latest_message = Communication.objects.filter(
                parent_id=chat_user.id,
                tutor_id=user.id
            ).order_by('-chat_id').first()
        
        if latest_message:
            conversations.append({
                'user': chat_user,
                'latest_message': latest_message
            })
    
    return render(request, 'app/chat_inbox.html', {
        'conversations': conversations
    })

@login_required
def chat_room(request, user_id):
    """View for displaying chat room with a specific user"""
    try:
        chat_user = User.objects.get(id=user_id)
        
        # Verify that users can chat (parent-tutor relationship)
        if (request.user.user_role == 'PARENT' and chat_user.user_role != 'TUTOR') or \
           (request.user.user_role == 'TUTOR' and chat_user.user_role != 'PARENT'):
            messages.error(request, 'Invalid chat user.')
            return redirect('app:chat_inbox')
        
        # Get parent and tutor objects
        if request.user.user_role == 'PARENT':
            parent = Parent.objects.get(user=request.user)
            tutor = Tutor.objects.get(user=chat_user)
        else:  # TUTOR
            parent = Parent.objects.get(user=chat_user)
            tutor = Tutor.objects.get(user=request.user)
        
        # Get chat history - get all messages between these two users
        chat_messages = Communication.objects.filter(
            parent=parent,
            tutor=tutor
        ).order_by('created_at')
        
        return render(request, 'app/chat_room.html', {
            'chat_user': chat_user,
            'messages': chat_messages
        })
        
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('app:chat_inbox')

@login_required
def send_message(request):
    """AJAX view for sending messages"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        receiver_id = request.POST.get('receiver_id')
        message_text = request.POST.get('message', '').strip()
        
        if not receiver_id or not message_text:
            return JsonResponse({'error': 'Both receiver and message are required.'}, status=400)
        
        receiver = User.objects.get(id=receiver_id)
        
        # Verify that users can chat (parent-tutor relationship)
        if (request.user.user_role == 'PARENT' and receiver.user_role != 'TUTOR') or \
           (request.user.user_role == 'TUTOR' and receiver.user_role != 'PARENT'):
            return JsonResponse({'error': 'Invalid chat user.'}, status=400)
        
        # Get parent and tutor objects
        if request.user.user_role == 'PARENT':
            parent = Parent.objects.get(user=request.user)
            tutor = Tutor.objects.get(user=receiver)
        else:  # TUTOR
            parent = Parent.objects.get(user=receiver)
            tutor = Tutor.objects.get(user=request.user)
        
        # Create message
        message = Communication.objects.create(
            parent=parent,
            tutor=tutor,
            message=message_text,
            user_role=request.user.user_role
        )
        
        # Return message data for immediate display
        return JsonResponse({
            'success': True,
            'message': message_text,
            'user_role': request.user.user_role,
            'created_at': message.created_at.strftime('%I:%M %p')
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Parent.DoesNotExist:
        return JsonResponse({'error': 'Parent not found'}, status=404)
    except Tutor.DoesNotExist:
        return JsonResponse({'error': 'Tutor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def start_chat(request, user_id):
    """View for starting a chat from tutor profile or student list"""
    try:
        other_user = User.objects.get(id=user_id)
        
        # Verify that users can chat (parent-tutor relationship)
        if (request.user.user_role == 'PARENT' and other_user.user_role != 'TUTOR') or \
           (request.user.user_role == 'TUTOR' and other_user.user_role != 'PARENT'):
            messages.error(request, 'Invalid chat user.')
            return redirect('app:chat_inbox')
        
        return redirect('app:chat_room', user_id=user_id)
        
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('app:chat_inbox')

@login_required
def parent_feedback(request):
    if request.method == 'POST':
        try:
            tutor_id = request.POST.get('tutor')
            schedule_id = request.POST.get('schedule_id')
            comments = request.POST.get('comments')
            flagged = request.POST.get('flagged') == 'on'

            if not all([tutor_id, schedule_id, comments]):
                messages.error(request, "Please fill in all required fields.")
                return redirect('app:parent_feedback')

            # Get the parent and tutor
            parent = Parent.objects.get(user=request.user)
            tutor = Tutor.objects.get(user_id=tutor_id)

            # Get the schedule
            try:
                schedule = Schedule.objects.get(schedule_id=schedule_id)
                
                # Check if this is a confirmed booking with payment
                booking = Booking.objects.filter(
                    parent=parent,
                    tutor=tutor,
                    schedule=schedule,
                    booking_status='CONFIRMED'
                ).first()

                if not booking:
                    messages.error(request, "Invalid session selection. Session must be confirmed.")
                    return redirect('app:parent_feedback')

                # Check payment status
                payment = Payment.objects.filter(booking=booking).order_by('-created_at').first()
                if not payment or payment.payment_status != 'COMPLETED':
                    messages.error(request, "Invalid session selection. Session must be paid.")
                    return redirect('app:parent_feedback')

                # Get time slot
                time_slots = schedule.time_slots
                if not time_slots or not isinstance(time_slots, list) or len(time_slots) == 0:
                    messages.error(request, "Invalid session time slots.")
                    return redirect('app:parent_feedback')
                
                time_slot = time_slots[0] if isinstance(time_slots, list) else time_slots

                # Check if feedback already exists
                existing_feedback = Feedback.objects.filter(
                    parent=parent,
                    tutor=tutor,
                    subject_name=schedule.subject,
                    comments__contains=time_slot  # Store time slot in comments since session_time is not used
                ).exists()

                if existing_feedback:
                    messages.error(request, "You have already submitted feedback for this session.")
                    return redirect('app:parent_feedback')

                # Format the time slot nicely
                if isinstance(time_slot, dict):
                    formatted_time = time_slot  # Keep the dictionary format for better parsing
                else:
                    try:
                        # Try to parse as JSON if it's a string
                        formatted_time = json.loads(time_slot)
                    except (json.JSONDecodeError, TypeError):
                        formatted_time = str(time_slot)

                # Create feedback with formatted time slot
                feedback = Feedback(
                    parent=parent,
                    tutor=tutor,
                    subject_name=schedule.subject,
                    comments=comments,  # Store only the user's comments
                    session_time=booking.session_time,  # Store the session time separately
                    flagged=flagged
                )
                feedback.save()

                messages.success(request, 'Feedback submitted successfully!')
                return redirect('app:parent_feedback')
            except Schedule.DoesNotExist:
                messages.error(request, "Invalid session selection.")
                return redirect('app:parent_feedback')

        except Exception as e:
            messages.error(request, f'Error submitting feedback: {str(e)}')
            return redirect('app:parent_feedback')

    # GET request - show form
    try:
        parent = Parent.objects.get(user=request.user)

        # Get confirmed bookings with payments
        completed_payments = Payment.objects.filter(
            booking__parent=parent,
            payment_status='COMPLETED'
        ).select_related(
            'booking',
            'booking__tutor',
            'booking__schedule'
        )

        print(f"Found {completed_payments.count()} completed payments")
        
        # Group bookings by tutor and subject
        tutor_classes = {}
        
        for payment in completed_payments:
            booking = payment.booking
            print(f"\nProcessing booking {booking.booking_id}:")
            print(f"- Subject: {booking.subject_name}")
            print(f"- Tutor: {booking.tutor.tutor_name}")
            print(f"- Status: {booking.booking_status}")
            
            # Skip if booking is not confirmed
            if booking.booking_status != 'CONFIRMED':
                print(f"- Skipping: Not confirmed")
                continue

            # Skip if no schedule
            if not booking.schedule:
                print(f"- Skipping: No schedule")
                continue

            # Get time slots
            schedule = booking.schedule
            print(f"- Schedule ID: {schedule.schedule_id}")
            print(f"- Raw time_slots: {schedule.time_slots}")

            # Convert time slots to list if needed
            time_slots = []
            raw_slots = schedule.time_slots

            if isinstance(raw_slots, str):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(raw_slots)
                    if isinstance(parsed, list):
                        time_slots = parsed
                    elif isinstance(parsed, dict):
                        time_slots = list(parsed.values())
                    else:
                        time_slots = [raw_slots]
                except json.JSONDecodeError:
                    time_slots = [raw_slots]
            elif isinstance(raw_slots, dict):
                time_slots = list(raw_slots.values())
            elif isinstance(raw_slots, list):
                time_slots = raw_slots
            else:
                time_slots = [str(raw_slots)]

            # Skip if no valid time slots
            if not time_slots:
                print(f"- Skipping: No time slots found")
                continue

            print(f"- Processed time slots: {time_slots}")

            # Create key for tutor-subject grouping
            key = f"{booking.tutor.user.id}_{booking.subject_name}"
            print(f"- Using key: {key}")
            
            # Initialize tutor-subject group if needed
            if key not in tutor_classes:
                tutor_classes[key] = {
                    "tutor": booking.tutor,
                    "subject_name": booking.subject_name,
                    "sessions": []
                }
            
            # Add each time slot as a session
            for slot in time_slots:
                if isinstance(slot, dict):
                    # Format the time slot in a readable way
                    weekday = slot.get('weekday', '')
                    start_time = slot.get('start_time', '')
                    end_time = slot.get('end_time', '')
                    formatted_time = f"{weekday} {start_time}:00 - {end_time}:00"
                else:
                    formatted_time = str(slot)

                session_data = {
                    "schedule_id": schedule.schedule_id,
                    "session_time": formatted_time,
                    "raw_data": slot  # Keep the raw data for reference
                }
                print(f"- Adding session: {session_data}")
                tutor_classes[key]["sessions"].append(session_data)

        # Convert sessions to JSON for template
        for key in tutor_classes:
            sessions_json = json.dumps(tutor_classes[key]["sessions"])
            print(f"\nJSON for {key}:")
            print(f"- Original sessions: {tutor_classes[key]['sessions']}")
            print(f"- JSON encoded: {sessions_json}")
            tutor_classes[key]["sessions"] = sessions_json

        if not tutor_classes:
            messages.info(request, "You don't have any confirmed and completed sessions to provide feedback for.")

        # Get previous feedbacks
        previous_feedbacks = Feedback.objects.filter(
            parent=parent
        ).select_related('tutor').order_by('-session_time')

        return render(request, 'app/parent_feedback.html', {
            'tutor_classes': tutor_classes.values(),
            'previous_feedbacks': previous_feedbacks
        })
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('app:parent_profile')

@login_required
def mark_notification_as_read(request, notification_id):
    """Mark a notification as read"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)
        
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    try:
        notification = UserNotification.objects.get(
            id=notification_id,
            user=request.user,
            is_read=False
        )
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        # Get updated unread count
        unread_count = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({
            'status': 'success',
            'unread_count': unread_count
        })
    except UserNotification.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Notification not found or already read'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def staff_feedback_review(request, feedback_id):
    if request.user.user_role != 'STAFF' and request.user.user_role != 'ADMIN':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')

    try:
        feedback = get_object_or_404(Feedback, feedback_id=feedback_id)
        
        if request.method == 'POST':
            # Update feedback status and notes
            feedback.status = request.POST.get('status')
            feedback.staff_notes = request.POST.get('staff_notes')
            feedback.flagged = request.POST.get('flagged') == 'on'
            feedback.reviewed_by = request.user
            feedback.save()

            # Send notification to the parent
            messages.success(request, f'Feedback #{feedback_id} has been updated successfully.')
        
        return redirect('app:staff_feedback')
        
    except Exception as e:
        logger.error(f"Error in staff_feedback_review view: {str(e)}")
        messages.error(request, "An error occurred while updating the feedback. Please try again.")
        return redirect('app:staff_feedback')

@login_required
def staff_feedback(request):
    if request.user.user_role != 'STAFF' and request.user.user_role != 'ADMIN':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('app:login')

    try:
        # Get filter parameters
        flagged_only = request.GET.get('flagged', '') == 'true'

        # Get feedback list with related data
        feedback_list = Feedback.objects.select_related(
            'parent',
            'tutor'
        ).all()

        # Apply filters
        if flagged_only:
            feedback_list = feedback_list.filter(flagged=True)

        # Order by creation date
        feedback_list = feedback_list.order_by('-created_at')

        context = {
            'title': 'Feedback Management',
            'feedback_list': feedback_list,
            'flagged_only': flagged_only
        }
        return render(request, 'app/staff_feedback.html', context)

    except Exception as e:
        logger.error(f"Error in staff_feedback view: {str(e)}")
        messages.error(request, "An error occurred while loading feedback data. Please try again.")
        return redirect('app:staff_profile')