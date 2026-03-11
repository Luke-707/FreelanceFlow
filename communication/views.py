from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Message, CallLog
from .forms import MessageForm

User = get_user_model()

@login_required
def chat_list(request):
    """List all users with whom the current user has chatted, with unread counts."""
    users = User.objects.exclude(id=request.user.id)

    # Annotate each user with the count of unread messages sent TO current user
    user_unread = {}
    for u in users:
        count = Message.objects.filter(
            sender=u, receiver=request.user, is_read=False
        ).count()
        user_unread[u.id] = count

    return render(request, 'communication/chat_list.html', {
        'users': users,
        'user_unread': user_unread,
    })

@login_required
def chat_detail(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    msgs = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    # Mark all received messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other_user
            msg.save()
            return redirect('chat_detail', user_id=user_id)
    else:
        form = MessageForm()

    return render(request, 'communication/chat_detail.html', {
        'other_user': other_user,
        'chat_messages': msgs,
        'form': form
    })

@login_required
def unread_count(request):
    """JSON endpoint: total unread messages for the logged-in user (used by navbar badge)."""
    count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def video_call(request, user_id):
    # Retrieve user to call
    callee = get_object_or_404(User, pk=user_id)

    # Just render the template with user info
    # In a real app, you'd create a CallLog entry here or via AJAX when connected
    CallLog.objects.create(caller=request.user, callee=callee)

    return render(request, 'communication/video_call.html', {
        'callee': callee,
        'room_id': f"{min(request.user.id, callee.id)}_{max(request.user.id, callee.id)}"
    })
