from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.contrib.auth import get_user_model

User = get_user_model()

class MyLoginAdapter(DefaultAccountAdapter):
    """Handles where to send the user after a successful login"""
    def get_login_redirect_url(self, request):
        user = request.user
        if hasattr(user, 'role'):
            if user.role == 'SELLER':
                return resolve_url('sellerhome')
            elif user.role == 'ADMIN':
                return resolve_url('admin_dashboard')
        return resolve_url('/')

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """Handles the connection between Social Media and Local Users"""
    def pre_social_login(self, request, sociallogin):
        # Skip if the account is already linked
        if sociallogin.is_existing:
            return

        # Check if email exists in our User table
        email = sociallogin.user.email
        if email:
            try:
                user = User.objects.get(email=email)
                # Manually connect the social account to the existing user
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass

    def save_user(self, request, sociallogin, form=None):
        """Called when creating a brand new user via Social Auth"""
        user = super().save_user(request, sociallogin, form)
        if not user.role:
            user.role = 'CUSTOMER'
            user.save()
        return user