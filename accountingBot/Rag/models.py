from django.db import models


# Create your models here.
class Params(models.Model):
    SystemPromptGerman = models.TextField()
    SystemPromptEnglish = models.TextField()
    temperature = models.FloatField()
    max_tokens = models.IntegerField(default=2000)


class Accounting(models.Model):
    SystemPromptGerman = models.TextField()
    SystemPromptEnglish = models.TextField()
    temperature = models.FloatField()
    max_tokens = models.IntegerField(default=2000)


class Taxes(models.Model):
    SystemPromptGerman = models.TextField()
    SystemPromptEnglish = models.TextField()
    temperature = models.FloatField()
    max_tokens = models.IntegerField(default=2000)


class ChatHistory(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    conversation_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.conversation_id
