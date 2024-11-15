from django.db import models
import uuid


# Create your models here.
class Params(models.Model):
    temperature = models.FloatField()
    max_tokens = models.IntegerField(default=2000)


class ChatSession(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_title = models.TextField()
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Session {self.session_id}"


class ChatHistory(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    message_user = models.TextField()
    message_bot = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # This automatically adds the current datetime

    def __str__(self):
        return f"Chat Session {self.session}"

