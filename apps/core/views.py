from django.views.generic import TemplateView
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from pytube import YouTube
from django.shortcuts import render, redirect
from django.views import View
from pytube.exceptions import PytubeError
from django.urls import reverse

from web_project import TemplateLayout
from django.conf import settings
from .models import Video

import os, requests

download_progress = {'progress': 0}

class CoreView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['YT_API_KEY'] = settings.YT_API_KEY
        return context
    

class YTSearchView(CoreView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')  # Get the search query from the request
        search_results = []

        if query:
            api_key = settings.YT_API_KEY
            api_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={query}&key={api_key}&maxResults=5"

            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                search_results = data.get('items', [])

        context = self.get_context_data(search_results=search_results)
        return render(request, 'yt_search.html', context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['YT_API_KEY'] = settings.YT_API_KEY
        return context


class DownloadYtView(CoreView):
    def get(self, request, *args, **kwargs):
        video_id = request.GET.get('video_id')  
        print(video_id)
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = None

        try:
            yt = YouTube(url)

            video_info = {
                'title': yt.title,
                'thumbnail': yt.thumbnail_url,
                'channelTitle': yt.author,
                'description': yt.description,
                'status': 'waiting'  # Initial status
            }

            context = self.get_context_data(video_info=video_info, video_id=video_id)
            response = render(request, 'download_video.html', context)
        except PytubeError as e:
            print(f"PytubeError: {e}")
            context = self.get_context_data(video_info={'status': 'error', 'error_message': 'Failed to retrieve video information.'})
            response = render(request, 'download_video.html', context)
        except Exception as e:
            print(f"General Error: {e}")
            context = self.get_context_data(video_info={'status': 'error', 'error_message': str(e)})
            response = render(request, 'download_video.html', context)

        return response
    def post(self, request):
        video_id = request.POST.get('video_id')
        url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(
            url,
            on_progress_callback=self.progress_download,
            on_complete_callback=self.complete_download,
            use_oauth=False,
            allow_oauth_cache=True
        )
        
        video_path = os.path.join(settings.MEDIA_ROOT, 'videos', f"{yt.title}.mp4")
        
        # Check if the video has already been downloaded
        if os.path.exists(video_path):
            video_info = {
                'title': yt.title,
                'thumbnail': yt.thumbnail_url,
                'channelTitle': yt.author,
                'description': yt.description,
                'status': 'already_downloaded'
            }
            context = self.get_context_data(video_info=video_info, video_id=video_id)
            return render(request, 'download_video.html', context)

        try:
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path=os.path.dirname(video_path), filename=os.path.basename(video_path))
            
            video_info = {
                'title': yt.title,
                'thumbnail': yt.thumbnail_url,
                'channelTitle': yt.author,
                'description': yt.description,
                'status': 'downloading'
            }
            
            new_video = Video(
                user=request.user,
                video_url=video_path,
                youtube_url=url,
                source_type='youtube',
                title=yt.title,
                description=yt.description,
            )
            new_video.save()

            print(new_video)

            context = self.get_context_data(video_info=video_info, video_id=video_id)
            return render(request, 'download_video.html', context)

        except Exception as e:
            # Handle the error, log it, or display a message
            print(f"Error downloading video: {e}")
            context = self.get_context_data(video_info={'title': yt.title, 'status': 'error', 'error_message': str(e)})
            return render(request, 'download_video.html', context)
        
    def download_video(self, video_id):
        url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(url, on_progress_callback=self.progress_download, on_complete_callback=self.complete_download)
        
        video_path = os.path.join(settings.MEDIA_ROOT, 'videos', f"{yt.title}.mp4")
        
        if os.path.exists(video_path):
            download_progress['progress'] = 100  # Video already downloaded
            return
        
        stream = yt.streams.get_highest_resolution()
        stream.download(output_path=os.path.dirname(video_path), filename=os.path.basename(video_path))

    def progress_download(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        download_progress['progress'] = percentage_of_completion

    def complete_download(self, stream, file_path):
        download_progress['progress'] = 100


class GetProgressView(View):
    def get(self, request):
        progress = download_progress.get('progress', 0)
        progress_percentage = f"{int(progress)}%"
        response_code = 200

        # Create the updated progress bar HTML with the dynamic width and inner text
        progress_bar = f"""
        <div class="progress-bar" 
             role="progressbar" 
             style="width: {progress}%;"
             id="downloadProgressBar">
             {progress_percentage}
        </div>
        """

        # Update response code to 286 when the progress reaches 100%
        if progress == 100:
            response_code = 286

        # Return the updated progress bar HTML directly
        return JsonResponse({'progress_bar': progress_bar}, status=response_code)
