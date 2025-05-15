from django import template
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key"""
    return dictionary.get(key, 'secondary')  # Return 'secondary' as default color

@register.filter
def get_payment_status_class(payment_status):
    if payment_status == 'COMPLETED':
        return 'success'
    elif payment_status == 'PENDING':
        return 'warning'
    elif payment_status == 'FAILED':
        return 'danger'
    return 'secondary'

@register.filter
def split(value, arg):
    """Split a string by the given argument"""
    return value.split(arg)

@register.filter
def filter(value, arg):
    """Get items at specified indices (comma-separated) from a list"""
    try:
        indices = [int(i) for i in arg.split(',')]
        return [value[i] for i in indices if i < len(value)]
    except (ValueError, IndexError, AttributeError):
        return []

@register.filter
def is_paid(booking):
    """Check if a booking has been paid"""
    return booking.payment_set.filter(payment_status='COMPLETED').exists()

@register.filter
def is_valid_for_payment(booking):
    """Check if a booking is valid for payment"""
    return booking.booking_status == 'CONFIRMED' and not is_paid(booking)

@register.filter
def split_string(value, index):
    """Split a string by space and return the item at the specified index"""
    try:
        return value.split()[int(index)]
    except (IndexError, ValueError, AttributeError):
        return ''

@register.filter
def format_time_slot(value):
    try:
        # Try to extract time slot info from the comments
        if isinstance(value, str):
            if "Time Slot:" in value:
                # Extract the time slot part
                time_slot_str = value.split("Time Slot:")[1].split("\n")[0].strip()
                try:
                    # Try to parse as JSON
                    time_slot = json.loads(time_slot_str)
                except json.JSONDecodeError:
                    time_slot = time_slot_str
            else:
                return value
        else:
            time_slot = value

        if isinstance(time_slot, dict):
            weekday = time_slot.get('weekday')
            start_time = time_slot.get('start_time')
            end_time = time_slot.get('end_time')
            
            if all([weekday, start_time, end_time]):
                return f"{weekday} {start_time} - {end_time}"
            
        return str(time_slot)
    except Exception:
        return str(value)
