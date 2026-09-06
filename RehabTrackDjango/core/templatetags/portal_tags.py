from django import template
from core.models import Notifications

register = template.Library()

@register.simple_tag
def unread_notifications_count(user):
    if user.is_authenticated:
        return Notifications.objects.filter(user_id=user, is_read=False).count()
    return 0
