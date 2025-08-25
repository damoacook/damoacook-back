from django.urls import path
from .views import NewsListCreateView, NewsRetrieveUpdateDestroyView

urlpatterns = [
    path('',        NewsListCreateView.as_view(),           name='news-list-create'),
    path('<int:id>/', NewsRetrieveUpdateDestroyView.as_view(), name='news-detail-update-delete'),
]