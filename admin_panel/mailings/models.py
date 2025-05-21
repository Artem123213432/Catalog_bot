from django.db import models

class Client(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.chat_id)

    class Meta:
        app_label = 'mailings'

class Mailing(models.Model):
    message_text = models.TextField()
    photo_id = models.CharField(max_length=255, blank=True, null=True)
    scheduled_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Mailing {self.id} at {self.scheduled_time}"

    class Meta:
        app_label = 'mailings'

