from django.urls import path
from .views import GalleryListCreateView, GalleryRetrieveDestroyView

urlpatterns = [
    path('',       GalleryListCreateView.as_view(),    name='gallery-list-create'),
    path('<int:id>/', GalleryRetrieveDestroyView.as_view(), name='gallery-detail-delete'),
]