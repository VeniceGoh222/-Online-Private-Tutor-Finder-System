from .models import UserNotification

def notifications(request):
    """Add notifications to template context"""
    if request.user.is_authenticated:
        user_notifications = UserNotification.objects.select_related('notification').filter(
            user=request.user
        ).order_by('-created_at')[:5]
        unread_count = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {
            'notifications': user_notifications,
            'unread_notifications_count': unread_count
        }
    return {
        'notifications': [],
        'unread_notifications_count': 0
    }
