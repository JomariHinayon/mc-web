from django.urls import path
from .views import CoreView


urlpatterns = [
    path(
        "",
        CoreView.as_view(template_name="index.html"),
        name="index",
    ),
    path(
        "",
        CoreView.as_view(template_name="index.html"),
        name="application",
    ),
    path(
        "yt-download",
        CoreView.as_view(template_name="page_2.html"),
        name="yt-download",
    ),
    path(
        "saved-videos",
        CoreView.as_view(template_name="page_2.html"),
        name="saved-videos",
    ),
    path(
        "projects",
        CoreView.as_view(template_name="page_2.html"),
        name="projects",
    ),
]
