from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse

from auth.views import AuthView


class LoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("index")  # Replace 'index' with the actual URL name for the home page
        else:
            return redirect("auth-login-basic")
        # Render the login page for users who are not logged in.
        return super().get(request)

    def post(self, request):
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            if not (email and password):
                messages.error(request, "Please enter your email and password.")
                return redirect("login")

            if "@" in email:
                user_email = User.objects.filter(email=email).first()
                if user_email is None:
                    messages.error(request, "Please enter a valid email.")
                    return redirect("login")
                email = user_email.email

            authenticated_user = authenticate(request, username=user_email.username, password=password)
            if authenticated_user is not None:
                # Login the user if authentication is successful
                login(request, authenticated_user)

                # Redirect to the page the user was trying to access before logging in
                if "next" in request.POST:
                    return redirect(request.POST["next"])
                else: # Redirect to the home page or another appropriate page
                    return redirect("index")
            else:
                messages.error(request, "Please enter a valid password.")
                return redirect("login")


class LoginAPIView(AuthView):

    def post(self, request):
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            # Check if both email and password are provided
            if not email or not password:
                return JsonResponse({"status": "error", "message": "Both email and password are required."}, status=400)

            # Check for valid email format and retrieve associated user if it exists
            if "@" in email:
                user_email = User.objects.filter(email=email).first()
                if user_email is None:
                    return JsonResponse({"status": "error", "message": "No account found with this email."}, status=404)
                email = user_email.email
            else:
                return JsonResponse({"status": "error", "message": "Please enter a valid email address."}, status=400)

            # Authenticate user
            authenticated_user = authenticate(request, username=user_email.username, password=password)
            if authenticated_user:
                # Log the user in if authentication succeeds
                login(request, authenticated_user)

                # Respond with success and redirect URL if provided
                next_url = request.POST.get("next", "index")
                return JsonResponse({"status": "success", "message": "Login successful.", "redirect_url": next_url}, status=200)
            else:
                return JsonResponse({"status": "error", "message": "Invalid password."}, status=400)