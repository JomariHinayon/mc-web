from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.http import HttpResponse, Http404
import subprocess
import os


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to sample/urls.py file for more pages.
"""


class CoreView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


def download_video(request, video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    file_path = f"{video_id}.mp4"

    # Use youtube-dl to download the video
    try:
        subprocess.run(['youtube-dl', '-f', 'best', '-o', file_path, url], check=True)
    except subprocess.CalledProcessError:
        return Http404("Video could not be downloaded.")

    # Check if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{video_id}.mp4"'
            return response
    else:
        raise Http404("File not found.")
