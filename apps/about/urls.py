from django.urls import path
from .views import AboutDetailView

urlpatterns = [
    path('', AboutDetailView.as_view(), name='about-detail'),
]