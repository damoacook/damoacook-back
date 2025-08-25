from django.urls import path
from .views import GalleryListCreateView, GalleryRetrieveUpdateDestroyView

urlpatterns = [
    path("", GalleryListCreateView.as_view(), name="gallery-list-create"),
    path(
        "<int:id>/",
        GalleryRetrieveUpdateDestroyView.as_view(),
        name="gallery-detail-delete",
    ),
]
