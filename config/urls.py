from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from apps.pages import views
import apps.companies.views
from django.views.static import serve

handler404 = 'apps.pages.views.error_404'
handler500 = 'apps.pages.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.pages.urls')),
    path('', include('apps.dyn_dt.urls')),
    path('', include('apps.dyn_api.urls')),
    path('', include('apps.react.urls')),
    path('charts/', include('apps.charts.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('', include('apps.file_manager.urls')),
    path('company/', include('apps.companies.urls')),
    path("users/", include("apps.users.urls")),
    path('auth/', include('apps.auth.urls')),
    path('checkout/', include('apps.checkouts.urls')),
    path('stripe/webhook/', apps.companies.views.stripe_webhook, name='stripe_webhook'),
    path('accounts/', include('allauth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 

    # Debug toolbar
    path("__debug__/", include("debug_toolbar.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path('i18n/', views.i18n_view, name="i18n_view")
)
