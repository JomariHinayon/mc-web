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
        "my-videos",
        CoreView.as_view(template_name="my_videos.html"),
        name="my_videos",
    ),
    path(
        "yt-download",
        CoreView.as_view(template_name="yt_download.html"),
        name="yt_download",
    ),
    path(
        "projects",
        CoreView.as_view(template_name="page_2.html"),
        name="projects",
    ),
]
