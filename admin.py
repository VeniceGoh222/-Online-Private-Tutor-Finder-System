from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Tutor, Parent, Staff, Administrator, Booking, Feedback, Payment, Communication, Schedule, SupportAssistance

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_phone_num', 'user_role', 'profile_status')
    list_filter = ('user_role', 'profile_status')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'user_phone_num')}),
        ('Roles', {'fields': ('user_role', 'profile_status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_phone_num', 'user_role', 'password1', 'password2'),
        }),
    )

# Register all models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Tutor)
admin.site.register(Parent)
admin.site.register(Staff)
admin.site.register(Administrator)
admin.site.register(Booking)
admin.site.register(Feedback)
admin.site.register(Payment)
admin.site.register(Communication)
admin.site.register(Schedule)
admin.site.register(SupportAssistance)
