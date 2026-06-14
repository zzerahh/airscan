from django.contrib import admin
from django.urls import path, include

# Custom error handlers
handler400 = 'inventory.views.bad_request'
handler403 = 'inventory.views.permission_denied'
handler404 = 'inventory.views.page_not_found'
handler500 = 'inventory.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
]