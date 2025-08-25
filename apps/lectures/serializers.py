from rest_framework import serializers
from apps.lectures.models import Lecture
from datetime import date


class LectureDisplaySerializer(serializers.ModelSerializer):
    remain = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = (
            'id',
            'title',
            'description',
            'image',
            'day_of_week',
            'time',
            'tags',
            'start_date',
            'end_date',
            'created_at',
            'remain',
            'status',
            'days_left',
        )

    def get_remain(self, obj):
        if obj.capacity is not None and obj.applied is not None:
            return max(obj.capacity - obj.applied, 0)
        return None

    def get_status(self, obj):
        today = date.today()
        if obj.end_date and obj.end_date < today:
            return "마감"
        elif obj.capacity is not None and obj.applied is not None and obj.capacity <= obj.applied:
            return "모집마감"
        return "진행중"

    def get_days_left(self, obj):
        today = date.today()
        if obj.end_date and obj.end_date >= today:
            return (obj.end_date - today).days
        return 0


class LectureCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'
