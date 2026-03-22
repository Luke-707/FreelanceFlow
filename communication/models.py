from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True, help_text="Optional file attachment")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"

    class Meta:
        ordering = ['timestamp']

class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='chat_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_image(self):
        name = self.file.name.lower()
        return name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))


class CallLog(models.Model):
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='calls_initiated', on_delete=models.CASCADE)
    callee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='calls_received', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True) # Duration in timedelta
    
    def __str__(self):
        return f"Call {self.caller} -> {self.callee}"
