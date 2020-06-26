from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from justchat.models import Room, ChatHistory
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


# def index(request):
#     return render(request, 'chat/index.html')
#
#
# def login(request):
#     return render(request, 'chat/login.html')
#
#
# def room(request, room_name):
#     return render(request, 'chat/room.html', {
#         'room_name': room_name
#     })


# @login_required
# def omchat(request):
#     rooms = Room.objects.order_by("title")
#     return render(request, 'chat/omchat.html', {
#         'rooms': rooms
#     })


@login_required
def userchat(request):
    print(f"user: ", request.user)
    a_user = User.objects.get(username=request.user)
    users = User.objects.exclude(username=a_user.username).order_by('id')
    print("a_user:", a_user.id)
    return render(request, 'userchat/user_chat.html', {
        'users': users,
        'a_user': a_user
    })


def chat_history(request):
    a_user_id = request.GET.get('a_user_id')
    b_user_id = request.GET.get('b_user_id')
    print(f"a_user_id {a_user_id}")
    print(f"b_user_id {b_user_id}")
    a_user = User.objects.get(pk=a_user_id)
    b_user = User.objects.get(pk=b_user_id)
    messages = ChatHistory.objects.filter(Q(a_party_user=a_user) | Q(a_party_user=b_user), Q(b_party_user=a_user) | Q(b_party_user=b_user)).order_by('created_at')
    return render(request, 'userchat/chat_history.html', {
        'a_user': a_user,
        'b_user': b_user,
        'messages': messages
    })


def send_chat(request):
    a_user_id = request.GET.get('a_user_id')
    b_user_id = request.GET.get('b_user_id')
    message = request.GET.get('message')
    print(f"a_user_id : {a_user_id}")
    print(f"b_user_id : {b_user_id}")
    print(f"message : {message}")

    ChatHistory.objects.create(a_party_user_id=a_user_id,
                               b_party_user_id=b_user_id,
                               message=message
                               )
    return HttpResponse("success")
