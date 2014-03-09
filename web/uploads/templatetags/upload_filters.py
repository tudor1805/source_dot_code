from django.template import Library

# Models
from uploads.models import User, Paste

# Code formatting
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

register = Library()

# Custom filters for handy stuff
@register.filter(name='times') 
def times(number):
    return range(1, number + 1)

@register.filter(name='get_num_lines') 
def get_num_lines(text):
    return text.count('\n') + 1

@register.filter(name='hl') 
def hl(text):
    return highlight(text, PythonLexer(), HtmlFormatter())

@register.filter(name='get_link') 
def get_link(paste):
    return 'http://localhost:8000/uploads/paste/' + paste.hash_id

