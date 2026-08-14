from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistrationForm
from .models import Profile


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            Profile.objects.create(user=user)

            login(request, user)

            return redirect("core:home")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )
