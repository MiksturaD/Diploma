from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def multiply(value, arg):
    # Преобразуем входные данные в float
    try:
        value = float(value)
        arg = float(arg)
        return value * arg
    except (ValueError, TypeError):
        return 0  # Если не удалось преобразовать, возвращаем 0