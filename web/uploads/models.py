from django.conf import settings
from django.db import models
from django.utils import timezone
#from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.utils.translation import gettext as _

class CustomUserManager(BaseUserManager):

    def _create_user(self, username, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
#        if not email:
#            raise ValueError('The given email must be set')
#        email = self.normalize_email(email)
        user = self.model(username=username,                          
                          is_staff=is_staff, is_active=True, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password, **extra_fields):
        return self._create_user(username, password, False, False, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    username   = models.CharField(max_length=254, unique=True, blank=True)
    email = models.EmailField(_('email address'), max_length=254, unique=False, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])
####


class Paste(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, default=None)
    time       = models.DateTimeField('Submit Date')
    hash_id    = models.CharField(max_length=20)
    language   = models.CharField(max_length=20)
    is_private = models.BooleanField()
    code       = models.TextField()
    output     = models.TextField()

    @classmethod
    def create(cls, hash_id, language, is_private, code, output):
        paste = cls(hash_id=hash_id, time=timezone.now(),language=language, is_private=is_private, code=code, output=output)
        # do something with the book
        return paste

    def __unicode__(self):
        return self.code

