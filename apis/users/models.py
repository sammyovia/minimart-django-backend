from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Add unique related_name arguments to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users_custom_user_set', # Unique related name for groups
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                    'granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='users_custom_user_permissions_set', # Unique related name for user_permissions
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # Example: add a phone number field if you want
    # phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)

    class Meta:
        # It's good practice to explicitly define the table name if you're
        # inheriting from AbstractUser, though not strictly necessary for this error.
        # This can help avoid confusion.
        db_table = 'users_user'