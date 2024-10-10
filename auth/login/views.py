from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
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
