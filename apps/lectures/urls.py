from django.urls import path
from .views import (
    AcademyLectureListView,
    AcademyLectureDetailView,
    AcademyLectureCreateView,
    AcademyLectureUpdateView,
)
from .views_hrd import (
    HRDLectureListView,
    HRDLectureDetailView,
)

urlpatterns = [
    # 내부 강의
    path('', AcademyLectureListView.as_view()),
    path('<int:id>/', AcademyLectureDetailView.as_view()),
    path('create/', AcademyLectureCreateView.as_view()),
    path('<int:id>/update/', AcademyLectureUpdateView.as_view()),

    # 고용24 강의
    path('hrd/', HRDLectureListView.as_view()),
    path('hrd/<str:trpr_id>/', HRDLectureDetailView.as_view()),
]