from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Return dictionary[key] safely in templates.

    Usage: {{ mydict|get_item:key }}
    """
    try:
        return dictionary.get(key) if hasattr(dictionary, 'get') else dictionary[key]
    except Exception:
        return None


@register.filter(name='score_badge')
def score_badge(score):
    """Return appropriate badge class based on score.
    
    Usage: {{ score|score_badge }}
    """
    try:
        score = float(score)
        if score >= 80:
            return 'success'
        elif score >= 60:
            return 'warning'
        else:
            return 'danger'
    except (ValueError, TypeError):
        return 'secondary'


@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply two numbers.
    
    Usage: {{ value|multiply:arg }}
    """
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
