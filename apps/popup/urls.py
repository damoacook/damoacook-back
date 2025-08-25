from django.urls import path
from .views import (
    PopupBannerListCreateView,
    PopupBannerRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('',         PopupBannerListCreateView.as_view(),             name='popup-list-create'),
    path('<int:id>/', PopupBannerRetrieveUpdateDestroyView.as_view(), name='popup-detail-update-delete'),
]