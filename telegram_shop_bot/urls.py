
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from shop_bot_app.views import main_page

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^webhooks/', include('shop_bot_app.urls')),
    url(r'^$', main_page),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
