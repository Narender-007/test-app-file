

# path('confirm-logout-old-session/', views.confirm_logout_old_session, name='confirm_logout_old_session'),
# path('cancel-logout-alert/', views.cancel_logout_alert, name='cancel_logout_alert'),

from django.contrib.auth import logout as django_logout
import hashlib

def logout(request):
    try:
        UserProfile.objects.filter(user=request.user).delete()
    except:
        pass
    django_logout(request)
    # request.session.clear()
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
   

    current_url = "{0}://{1}".format(request.scheme, request.get_host())
    return_to  = current_url
    # return_to  = 'http://localhost:4000'

    print(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}','76574645')
    return redirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')
    
# https://dev-3zlx9a5v.us.auth0.com/u/login?
# state=hKFo2SBJdWo2bzVNenNGdjEtYm9XcHRFVWdRRVNUUmFTUnh5aKFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIGlRXzhwLWI4Rld1RTh4MnRESkpWRGl0bnJG
# YnozSFM5o2NpZNkgMU1rTmdsYTVrT2Vhc0pzWFdVUzFRcmVzd0lURjBwNjQ
# https://dev-3zlx9a5v.us.auth0.com/v2/logout?client_id=1MkNgla5kOeasJsXWUS1QreswITF0p64&returnTo=http://localhost:4000

# def handle_logout_confirmation(request):
#     if request.session.get('confirm_logout', False):
#         user = request.user
#         current_session_key = request.session.session_key
#         current_user_agent = request.META.get('HTTP_USER_AGENT', '')

#         # Get or create user's profile
#         profile, created = UserProfile.objects.get_or_create(user=user, user_agent=current_user_agent)

#         # Step 1: Check if there is any active session on the same browser (same user-agent) with different user
#         active_profiles = UserProfile.objects.filter(user_agent=current_user_agent).exclude(user=user)

#         if active_profiles.exists():
#             messages.error(request, "⚠️ Another user is already logged in from this browser. Please logout first.")
#             request.session.flush()
#             return redirect('logout')

#         # Step 2: Check if same user already has another session active
#         if profile.session_key and profile.session_key != current_session_key:
#             messages.error(request, "⚠️ You are already logged in elsewhere. Please logout from the previous session first.")
#             request.session.flush()
#             return redirect('logout')

#         # Step 3: If everything is okay, update profile
#         profile.session_key = current_session_key
#         profile.user_agent = current_user_agent
#         profile.save()

#         # Step 4: Clear flags
#         request.session.pop('confirm_logout', None)
#         request.session.pop('alert_message', None)

#         messages.success(request, "✅ You have logged in successfully!")
#         return redirect('scm_homepage')
from django.db.models import Q

def handle_logout_confirmation(request):
    if request.session.get('confirm_logout', False):
        user = request.user
        current_session_key = request.session.session_key
        current_user_agent = request.META.get('HTTP_USER_AGENT', '')
         # Step 4: Update this user's profile with new session key
        ip = request.META.get('REMOTE_ADDR', '')
        ua = request.META.get('HTTP_USER_AGENT', '')
        accept = request.META.get('HTTP_ACCEPT', '')
        encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')

        # Combine parts to build a more specific device signature
        raw_fingerprint = f"{ip}|{ua}|{accept}|{encoding}"
        device_fingerprint = hashlib.sha256(raw_fingerprint.encode()).hexdigest()
        # Step 1: Get or create current user profile
        profile, created = UserProfile.objects.get_or_create(user=user)

        # Step 2: Check if this user's old session needs to be deleted
        if profile.session_key and profile.session_key != current_session_key:
            previous_session = Session.objects.filter(session_key=profile.session_key).first()
            if previous_session:
                previous_session.delete()

        # Step 3: 🚨 Kill any OTHER user sessions with same User-Agent
        other_profiles = UserProfile.objects.filter(
            ~Q(user=user),
            user_agent=device_fingerprint,
            is_active=True
        )

        for other_profile in other_profiles:
            other_session = Session.objects.filter(session_key=other_profile.session_key).first()
            if other_session:
                other_session.delete()  # ❌ Kill other user's session
            other_profile.is_active = False
            other_profile.session_key = None
            other_profile.device_fingerprint = None
            other_profile.save()

       
        profile.session_key = current_session_key
        profile.user_agent = device_fingerprint
        profile.is_active = True
        profile.save()

        # Step 5: Clear session flags
        if 'confirm_logout' in request.session:
            del request.session['confirm_logout']
        if 'alert_message' in request.session:
            del request.session['alert_message']


    return redirect('scm_homepage')
from django.http import JsonResponse
def check_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    return JsonResponse({'status': 'OK','username': request.user.username})


def check_store_change(request):
    store_changed = request.session.get('store_changed', False)
    return JsonResponse({'store_changed': store_changed})



def confirm_logout_old_session(request):
    current_session_key = request.session.session_key
    current_user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Fetch all active profiles from this browser
    active_profiles = UserProfile.objects.filter(user_agent=current_user_agent, is_active=True)
    user = request.user
    for profile in active_profiles:
        if not Session.objects.filter(session_key=profile.session_key).exists():
            profile.is_active = False
            profile.save()
            continue

        if profile.user != user:
            try:
                Session.objects.get(session_key=profile.session_key).delete()
            except Session.DoesNotExist:
                pass
            
        elif profile.user == user and profile.session_key != current_session_key:
            # Same user: kill old session
            try:
                Session.objects.get(session_key=profile.session_key).delete()
            except Session.DoesNotExist:
                pass

    return JsonResponse({'status': 'ok'})

def cancel_logout_alert(request):
    # Just remove the flags
    request.session.pop('confirm_logout', None)
    request.session.pop('alert_message', None)
    request.session.pop('old_session_key', None)
    return JsonResponse({'status': 'cancelled'})

