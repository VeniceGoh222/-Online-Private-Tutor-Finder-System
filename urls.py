from django.urls import path
from . import views
from datetime import datetime
from django.conf import settings
from django.conf.urls.static import static

app_name = 'app'

urlpatterns = [
    path('', views.index, name='home'),
    path('role-select/', views.role_select, name='role_select'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('register/parent/', views.register_parent, name='register_parent'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('menu/', views.menu, name='menu'),
    path('parent/profile/', views.parent_profile, name='parent_profile'),
    path('parent/profile/edit', views.edit_parent_profile, name='edit_parent_profile'),
    path('parent/search/', views.parent_search, name='parent_search'),
    path('parent/booking/', views.parent_booking, name='parent_booking'),
    path('parent/payment/', views.parent_payment, name='parent_payment'),
    path('parent/payment/details/', views.parent_payment_details, name='parent_payment_details'),
    path('parent/schedule/', views.parent_schedule, name='parent_schedule'),
    path('parent/feedback/', views.parent_feedback, name='parent_feedback'),
    path('parent/add/favorite', views.parent_add_favorite, name='parent_add_favorite'),
    path('parent/delete-favorite/<int:favorite_id>/', views.delete_favorite_tutor, name='delete_favorite_tutor'),
    path('parent/view/tutor/<int:pk>/', views.parent_view_tutor_profile, name='parent_view_tutor_profile'),

    path('register/tutor/', views.register_tutor, name='register_tutor'),
    path('tutor/profile/', views.tutor_profile, name='tutor_profile'),
    path('tutor/profile/edit/', views.edit_tutor_profile, name='edit_tutor_profile'),
    path('tutor/booking/', views.tutor_booking, name='tutor_booking'),
    path('tutor/payment/', views.tutor_payment, name='tutor_payment'),
    path('tutor/schedule/', views.tutor_schedule, name='tutor_schedule'),
    path('tutor/student/', views.tutor_student, name='tutor_student'),
    path('tutor/feedback/', views.tutor_feedback, name='tutor_feedback'),
    path('tutor/create_class/', views.tutor_create_class, name='tutor_create_class'),
    path('tutor/view_classes/', views.tutor_view_classes, name='tutor_view_classes'),
    path('tutor/update_class/<int:class_id>/', views.tutor_update_class, name='tutor_update_class'),
    path('tutor/classes/<int:class_id>/delete/', views.tutor_delete_class, name='tutor_delete_class'),
    path('tutor/report/', views.tutor_report, name='tutor_report'),
    path('tutor/send_feedback/<int:booking_id>/', views.tutor_send_feedback, name='tutor_send_feedback'),
    path('report/', views.report, name='report'),
    
    # Admin URLs
    path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('admin_administration/', views.admin_administration, name='admin_administration'),
    path('admin_user_management/', views.admin_user_management, name='admin_user_management'),
    path('admin_user_management/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin_payment_management/', views.admin_payment_management, name='admin_payment_management'),
    
    # Admin tutor management
    path('admin_tutor_management/', views.admin_tutor_management, name='admin_tutor_management'),
    path('admin_tutor_management/tutor/<int:tutor_id>/details/', views.tutor_details, name='tutor_details'),
    path('admin_tutor_management/tutor/<int:tutor_id>/approve/', views.tutor_approve, name='tutor_approve'),
    path('admin_tutor_management/tutor/<int:tutor_id>/decline/', views.tutor_decline, name='tutor_decline'),
    path('admin_tutor_management/export/', views.admin_export_tutors, name='admin_export_tutors'),
    
    # Admin payment management
    path('admin_payment_management/export/', views.admin_export_payments, name='admin_export_payments'),
    path('admin_payment_management/report/', views.admin_generate_payment_report, name='admin_generate_payment_report'),
    
    # Staff URLs
    path('staff_profile/', views.staff_profile, name='staff_profile'),
    path('staff_support/', views.staff_support, name='staff_support'),
    path('staff_support/<int:query_id>/respond/', views.respond_to_support_query, name='respond_to_support_query'),
    path('staff_support/<int:query_id>/status/', views.update_support_query_status, name='update_support_query_status'),
    path('staff_data/', views.staff_data, name='staff_data'),
    path('staff_feedback/', views.staff_feedback, name='staff_feedback'),
    path('staff_notification/', views.staff_notification, name='staff_notification'),
    path('mark-notification-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    
    # Chat URLs
    path('chat/', views.chat_inbox, name='chat_inbox'),
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/start/<int:tutor_id>/', views.start_chat, name='start_chat'),
    
    # Notifications
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    
    # Staff feedback review
    path('staff/feedback/<int:feedback_id>/review/', views.staff_feedback_review, name='staff_feedback_review'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])