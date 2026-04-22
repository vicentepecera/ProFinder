from django import template
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def formato_telefono(value):
    if not value:
        return "No especificado"
    digits = re.sub(r'\D', '', str(value))
    if digits.startswith('56') and len(digits) == 11:
        digits = digits[2:]
    if digits.startswith('9') and len(digits) == 9:
        return f"+56 9 {digits[1:5]} {digits[5:]}"
    return value