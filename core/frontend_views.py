from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def library(request):
    return render(request, 'library.html')


def create_song(request):
    return render(request, 'create.html')


def song_detail(request, song_id):
    return render(request, 'song_detail.html', {'song_id': song_id})


def libraries_list(request):
    return render(request, 'libraries.html')


def library_detail_page(request, library_id):
    return render(request, 'library_detail_page.html', {'library_id': library_id})
