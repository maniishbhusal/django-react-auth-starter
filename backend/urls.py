from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls')), # Djoser core urls (users, activation, password reset)
    path('api/auth/', include('djoser.urls.jwt')), # Djoser JWT urls (token create/refresh - overrides simplejwt)
    # path('api/auth/', include('djoser.social.urls')), # If using Djoser's social auth integration
    path('api/auth/', include('allauth.urls')), # Allauth URLs for social login flows, account management etc.

    # Your other API endpoints
    # path('api/', include('your_other_app.urls')),
]

# In a production environment, static and media files are typically served by a dedicated web server (like Nginx or Apache) or a Content Delivery Network (CDN) for better performance and efficiency. Django's development server is not designed to handle static files efficiently in production.
# Therefore, the code within the if settings.DEBUG: block is only executed when the project is in development mode, allowing the development server to serve these files.
# In essence, this part of the code ensures that your static and media files are correctly served when you're working on your Django project locally, but it won't affect how they are handled in a production deployment.

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Only for dev