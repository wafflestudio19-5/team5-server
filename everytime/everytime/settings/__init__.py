# Reference : https://dev.to/vlntsolo/how-to-split-django-settings-for-different-environments-18ad
# Reference : https://akshaybabloo.medium.com/splitting-django-settings-for-local-and-production-development-c8f4a6ec1ad0

from .base import *

live = False

try:
    from .dev import *
except ImportError:
    live = True
if live:
    from .prod import *
