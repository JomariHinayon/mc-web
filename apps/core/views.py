from django.views.generic import TemplateView
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from pytube import YouTube
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from threading import Thread
from web_project import TemplateLayout
from django.conf import settings
import os

download_progress = {'progress': 0}

class CoreView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['YT_API_KEY'] = settings.YT_API_KEY
        return context


class DownloadYtView(CoreView):
    def get(self, request, video_id):
        url = f"https://www.youtube.com/watch?v={video_id}"
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
        return response

    def post(self, request, video_id):
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
                'status': 'downloading'  # Indicate that the download is in progress
            }

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
