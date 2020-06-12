from django.shortcuts import render

from justchat.models import Room


def index(request):
    return render(request, 'chat/index.html')


def login(request):
    return render(request, 'chat/login.html')


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })


def omchat(request):
    rooms = Room.objects.order_by("title")
    return render(request, 'chat/omchat.html', {
        'rooms': rooms
    })
