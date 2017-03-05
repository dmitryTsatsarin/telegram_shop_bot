
from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^webhooks/', include('shop_bot_app.urls')),
]
