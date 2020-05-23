__title__ = 'Flask-User'
__description__ = 'Customizable User Authentication, User Management, and more.'
__version__ = '1.0.2.3'
__url__ = 'https://github.com/lingthio/Flask-User'
__author__ = 'Ling Thio'
__author_email__ = 'ling.thio@gmail.com'
__maintainer__ = 'Ling Thio'
__license__ = 'MIT'
__copyright__ = '(c) 2013 Ling Thio'


# Define Flask-User Exceptions early on
class ConfigError(Exception):
    pass


class EmailError(Exception):
    pass


# Export Flask-Login's current user

# Export Flask-User decorators
from .decorators import *
from .email_manager import EmailManager
# Export v0.6 legacy classes DbAdapter and SQLAlchemyAdapter
# To display an Incompatibility error message the v0.6 API is used on a v1.0+ install
from .legacy_error import DbAdapter, SQLAlchemyAdapter
from .password_manager import PasswordManager
# Export Flask-User signals
from .signals import *
from .token_manager import TokenManager
from .user_manager import UserManager
from .user_mixin import UserMixin
