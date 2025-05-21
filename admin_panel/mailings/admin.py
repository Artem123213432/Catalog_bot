from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from .models import Client, Mailing

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('chat_id',)

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_message', 'scheduled_time', 'status_colored', 'sent_at', 'has_photo')
    list_filter = ('is_sent',)
    search_fields = ('message_text',)
    readonly_fields = ('sent_at',)
    actions = ['start_mailing']
    
    def short_message(self, obj):
        if len(obj.message_text) > 50:
            return f"{obj.message_text[:50]}..."
        return obj.message_text
    short_message.short_description = 'Текст сообщения'
    
    def status_colored(self, obj):
        if obj.is_sent:
            return format_html('<span style="color: green;">Отправлено</span>')
        return format_html('<span style="color: red;">Не отправлено</span>')
    status_colored.short_description = 'Статус'
    
    def has_photo(self, obj):
        if obj.photo_id:
            return format_html('✅')
        return format_html('❌')
    has_photo.short_description = 'Фото'

    def start_mailing(self, request, queryset):
        count = 0
        for mailing in queryset:
            from django.db import connection
            with connection.cursor() as cursor:
                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "UPDATE mailings_mailing SET is_sent = false, scheduled_time = %s, sent_at = NULL WHERE id = %s",
                    [now, mailing.id]
                )
            count += 1
            
        messages.success(request, f'{count} рассылок запущены. Бот проверяет новые рассылки каждые 15 секунд.')
    start_mailing.short_description = 'Запустить рассылку'
    
    def save_model(self, request, obj, form, change):
        obj.is_sent = False
        if not obj.scheduled_time:
            obj.scheduled_time = timezone.now()
        super().save_model(request, obj, form, change)
