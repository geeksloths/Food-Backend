from django.urls import path, include

from Category import api_views

urlpatterns = [
    path('', api_views.ListApi.as_view())
]
