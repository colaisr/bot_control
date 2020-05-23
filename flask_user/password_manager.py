"""This module implements the PasswordManager for Flask-User.
It uses passlib to hash and verify passwords.
"""

# Author: Ling Thio <ling.thio@gmail.com>
# Copyright (c) 2013 Ling Thio

from __future__ import print_function

from passlib.context import CryptContext


class PasswordManager(object):
    """Hash and verify user passwords using passlib """

    def __init__(self, app):
        """
        Create a passlib CryptContext.

        Args:
            password_hash(str): The name of a valid passlib password hash.
                Examples: ``'bcrypt', 'pbkdf2_sha512', 'sha512_crypt' or 'argon2'``.

        Example:
            ``password_manager = PasswordManager('bcrypt')``
        """

        self.app = app
        self.user_manager = app.user_manager

        # Create a passlib CryptContext
        self.password_crypt_context = CryptContext(
            schemes=self.user_manager.USER_PASSLIB_CRYPTCONTEXT_SCHEMES,
            **self.user_manager.USER_PASSLIB_CRYPTCONTEXT_KEYWORDS)

    def hash_password(self, password):
        """Hash plaintext ``password`` using the ``password_hash`` specified in the constructor.

        Args:
            password(str): Plaintext password that the user types in.
        Returns:
            hashed password.
        Example:
            ``user.password = hash_password('mypassword')``
        """

        # Use passlib's CryptContext to hash a password
        password_hash = self.password_crypt_context.hash(password)

        return password_hash

    def verify_password(self, password, password_hash):
        """Verify plaintext ``password`` against ``hashed password``.

        Args:
            password(str): Plaintext password that the user types in.
            password_hash(str): Password hash generated by a previous call to ``hash_password()``.
        Returns:
            | True when ``password`` matches ``password_hash``.
            | False otherwise.
        Example:

            ::

                if verify_password('mypassword', user.password):
                    login_user(user)
        """

        # Print deprecation warning if called with (password, user) instead of (password, user.password)
        if isinstance(password_hash, self.user_manager.db_manager.UserClass):
            print(
                'Deprecation warning: verify_password(password, user) has been changed' \
                ' to: verify_password(password, password_hash). The user param will be deprecated.' \
                ' Please change your call with verify_password(password, user) into' \
                ' a call with verify_password(password, user.password)'
                ' as soon as possible.')
            password_hash = password_hash.password  # effectively user.password

        # Use passlib's CryptContext to verify a password
        return self.password_crypt_context.verify(password, password_hash)
