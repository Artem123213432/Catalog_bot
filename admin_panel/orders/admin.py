from django.contrib import admin
from django.contrib import messages
from .models import Client, Order, Mailing

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'full_name', 'created_at')
    search_fields = ('telegram_id', 'username', 'full_name')
    list_filter = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'created_at', 'is_paid')
    list_filter = ('created_at', 'is_paid')
    search_fields = ('client__username', 'client__full_name', 'client__telegram_id')

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'sent')
    list_filter = ('sent',)
    search_fields = ('message',)
    actions = ['run_mailing'] # Меняем название действия

    @admin.action(description='Запустить рассылку') # Меняем описание
    async def run_mailing(self, request, queryset):
        # Отбираем только те рассылки, которые еще не были отправлены
        unsent_mailings = queryset.filter(sent=False)
        count = await unsent_mailings.acount()
        
        if not count:
            self.message_user(request, "Нет неотправленных рассылок для запуска.", messages.WARNING)
            return
        
        # Ничего не делаем здесь с флагом sent. Бот сам его обновит после отправки.
        self.message_user(request, f'{count} рассылок будут запущены.', messages.SUCCESS)

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 1 