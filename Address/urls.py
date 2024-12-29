from django.urls import path

from Address import views

urlpatterns = [
    path('', views.AddressListAPIView.as_view())
]
