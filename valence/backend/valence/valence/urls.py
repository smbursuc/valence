from django.urls import path, include

urlpatterns = [
    path('valence/', include('myapp.urls')),
]
