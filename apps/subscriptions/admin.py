from django.contrib import admin
from .models import Subscription, SubscriptionPrice, UserSubscription

class SubscriptionPriceInline(admin.StackedInline):
    model = SubscriptionPrice
    readonly_fields = ['stripe_id']
    can_delete = True
    extra = 0

class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionPriceInline]
    list_display = ['name', 'active']
    readonly_fields = ['stripe_id']

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSubscription)
