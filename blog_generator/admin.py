from django.contrib import admin
from .models import BlogPost, YouTubeAudioFile

# Register your models here.
admin.site.register(BlogPost)
admin.site.register(YouTubeAudioFile)