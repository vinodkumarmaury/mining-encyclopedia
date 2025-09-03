from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # convenience redirect so /profile works (maps to accounts app)
    path('profile/', RedirectView.as_view(url='/accounts/profile/', permanent=False)),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('tests/', include('tests.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)