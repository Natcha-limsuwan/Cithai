import json
import secrets
import urllib.parse

import requests as http_client
from django.conf import settings
from django.shortcuts import redirect, render

from .models import User

_GOOGLE_AUTH_URL     = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL    = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def google_login(request):
    if not settings.GOOGLE_CLIENT_ID:
        return redirect("/?error=Google+OAuth+is+not+configured+on+this+server")

    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    params = urllib.parse.urlencode({
        "client_id":     settings.GOOGLE_CLIENT_ID,
        "redirect_uri":  settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "state":         state,
        "access_type":   "online",
    })
    return redirect(f"{_GOOGLE_AUTH_URL}?{params}")


def google_callback(request):
    error = request.GET.get("error")
    if error:
        return redirect(f"/?error={urllib.parse.quote(error)}")

    # CSRF state check
    expected_state = request.session.pop("oauth_state", None)
    if not expected_state or request.GET.get("state") != expected_state:
        return redirect("/?error=Invalid+OAuth+state.+Please+try+again.")

    code = request.GET.get("code")
    if not code:
        return redirect("/?error=No+authorization+code+received.")

    # Exchange code for access token
    try:
        token_resp = http_client.post(_GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri":  settings.GOOGLE_REDIRECT_URI,
            "grant_type":    "authorization_code",
        }, timeout=10)
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]
    except Exception:
        return redirect("/?error=Failed+to+exchange+OAuth+token.")

    # Fetch user profile from Google
    try:
        info_resp = http_client.get(
            _GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        info_resp.raise_for_status()
        info = info_resp.json()
    except Exception:
        return redirect("/?error=Failed+to+fetch+Google+profile.")

    google_id = info.get("id", "")
    email     = info.get("email", "")
    name      = info.get("name", "")

    # Find existing user by google_id → email → create new
    user = User.objects.filter(google_id=google_id).first()
    if user is None:
        user = User.objects.filter(email=email).first()

    if user is None:
        base = (email.split("@")[0] or "user").replace(".", "_")
        username, n = base, 1
        while User.objects.filter(username=username).exists():
            username = f"{base}_{n}"
            n += 1
        user = User(username=username, email=email, name=name, google_id=google_id)
        user.set_unusable_password()
        user.save()
    else:
        user.google_id = google_id
        user.name = name
        user.save(update_fields=["google_id", "name"])

    # Pass user data to template — json.dumps handles escaping
    user_data = json.dumps({
        "user_id": user.user_id,
        "name":    user.name,
        "email":   user.email,
    })
    return render(request, "oauth_success.html", {"user_data": user_data})
