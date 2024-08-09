from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import BlogPost, YouTubeAudioFile
import os
from openai import OpenAI
from pytubefix import YouTube
from pytubefix.cli import on_progress
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

client = OpenAI(
    api_key=os.environ.get('OPENAI_KEY'),
)
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link, request.user)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)

        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': " Failed to generate blog article"}, status=500)

        # save blog article to database
        new_blog_article = BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )
        new_blog_article.save()

        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Получаем название ютуб видео
def yt_title(link):
    
    yt = YouTube(link, on_progress_callback = on_progress)
    return yt.title

def download_audio(link, user):
    
    # Проверяем, есть ли уже загруженный файл
    cached_file = get_cached_audio_file(link, user)
    if cached_file:
        return cached_file

    # Если нет, загружаем файл
    yt = YouTube(link, on_progress_callback=on_progress)
    ys = yt.streams.get_audio_only()
    out_file = ys.download(output_path=settings.MEDIA_ROOT,mp3=True)
    base, ext = os.path.splitext(out_file)
    new_file = base.replace(' ', '_') + '.mp3'
    os.rename(out_file, new_file)

    # Сохраняем информацию о загруженном файле в базу данных
    YouTubeAudioFile.objects.create(
        user=user,
        youtube_link=link,
        file_path=new_file
    )
    return new_file

# Транскрибируем ютуб видео для получения текста
def get_transcription(link, user):
    audio_file_path = download_audio(link, user)
    
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )

    return transcription

def generate_blog_from_transcription(transcription):

    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:Article: {transcription}"

    response = client.chat.completions.create(
        model="gpt-4o",  # Убедитесь, что указана правильная модель
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=4096,
        temperature=0.7,
    )
    message = response.choices[0].message.content
    return message

# логин для регистрации обязателен
@login_required
def index(request):
    return render(request, 'index.html')

# если POST метод то позволяем пользователю пройти регистрацию
def user_login(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message':error_message})
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def get_cached_audio_file(youtube_link, user):
    try:
        audio_file = YouTubeAudioFile.objects.get(youtube_link=youtube_link, user=user)
        return audio_file.file_path
    except YouTubeAudioFile.DoesNotExist:
        return None   
    
def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all_blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog_details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')
