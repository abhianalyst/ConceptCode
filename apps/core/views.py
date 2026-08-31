from django.shortcuts import render

from .models import Subject


def home(request):
    subjects = (
        Subject.objects
        .filter(
            is_active=True,
            chapters__is_active=True,
            chapters__topics__is_active=True,
            chapters__topics__questions__is_active=True,
        )
        .prefetch_related(
            "chapters__topics",
        )
        .distinct()
    )

    return render(
        request,
        "core/home.html",
        {
            "subjects": subjects,
        },
    )