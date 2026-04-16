from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse 
from django.shortcuts import redirect, resolve_url
from django.contrib.auth import get_user_model
from django.contrib import messages  

User = get_user_model()

def get_redirect_by_role(user):
    if hasattr(user, 'role'):
        if user.role == 'SELLER':
            return resolve_url('sellerhome')
        elif (user.role == 'ADMIN' or user.is_superuser):
            return resolve_url('admindashboard')
        elif user.role == 'CUSTOMER':
            return resolve_url('home')
    
    if user.is_superuser:
        return resolve_url('admindashboard')
        
    return resolve_url('home')

class MyLoginAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        return get_redirect_by_role(user)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # 1. Extract Email
        email = sociallogin.user.email or sociallogin.account.extra_data.get('email')

        if not email:
            messages.error(request, "Google account must have a verified email.")
            raise ImmediateHttpResponse(redirect('login'))

        try:
            user = User.objects.get(email=email)

            # 2. Block Admin Social Login
            if user.is_superuser or user.is_staff:
                messages.error(request, "Admin accounts must login using the standard form.")
                raise ImmediateHttpResponse(redirect('login'))

            # 3. RULE: Block unapproved Sellers (Added this part)
            if hasattr(user, 'role') and user.role == 'SELLER' and not user.is_active:
                messages.error(request, "You can login only after admin approves you.")
                raise ImmediateHttpResponse(redirect('login'))

            # 4. Connect existing account if not already connected
            if not sociallogin.is_existing:
                from allauth.socialaccount.models import SocialAccount
                if not SocialAccount.objects.filter(user=user, provider=sociallogin.account.provider).exists():
                    sociallogin.connect(request, user)

        except User.DoesNotExist:
            # New users can proceed to sign up via social account
            pass

    def get_connect_redirect_url(self, request, socialaccount):
        return get_redirect_by_role(request.user)