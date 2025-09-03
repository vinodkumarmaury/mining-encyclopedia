from django import template
import math

register = template.Library()

@register.filter
def reading_time(content):
    if not content:
        return 0
    words = len(content.split())
    minutes = max(1, math.ceil(words / 200))
    return minutes
