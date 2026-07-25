# backend/apps/moderation/serializers.py

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Report


class ReportCreateSerializer(serializers.ModelSerializer):
    """Юзер подає скаргу"""
    content_type_name = serializers.ChoiceField(
        choices=['post', 'comment'],
        write_only=True
    )
    object_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Report
        fields = ['content_type_name', 'object_id', 'reason', 'comment']

    def validate(self, attrs):
        ct_name = attrs.pop('content_type_name')
        object_id = attrs['object_id']

        if ct_name not in ('post', 'comment'):
            raise serializers.ValidationError('Невірний тип контенту')

        try:
            ct = ContentType.objects.get(
                app_label__in=['main', 'comments'], model=ct_name)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError('Тип контенту не знайдено')

        if not ct.get_object_for_this_type(pk=object_id):
            raise serializers.ValidationError('Обʼєкт не знайдено')

        attrs['content_type'] = ct
        return attrs

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class ReportAdminSerializer(serializers.ModelSerializer):
    """Адмін бачить повний репорт з інфо про автора і обʼєкт"""
    reporter_username = serializers.CharField(
        source='reporter.username', read_only=True)
    reviewed_by_username = serializers.CharField(
        source='reviewed_by.username', read_only=True, default=None
    )
    content_type_name = serializers.CharField(
        source='content_type.model', read_only=True)
    reason_display = serializers.CharField(
        source='get_reason_display', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    object_preview = serializers.SerializerMethodField()
    object_author = serializers.SerializerMethodField()
    # НОВЕ: slug для побудови правильного посилання на фронті
    object_slug = serializers.SerializerMethodField()
    # НОВЕ: для коментаря — slug поста до якого він належить
    object_post_slug = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'reporter_username', 'reason', 'reason_display',
            'comment', 'status', 'status_display',
            'content_type_name', 'object_id',
            'object_preview', 'object_author',
            'object_slug', 'object_post_slug',
            'reviewed_by_username', 'reviewed_at', 'admin_note',
            'created_at',
        ]

    def get_object_preview(self, obj):
        try:
            target = obj.content_object
            if target is None:
                return '(обʼєкт видалено)'
            text = getattr(target, 'title', None) or getattr(
                target, 'content', '')
            return str(text)[:120]
        except Exception:
            return '(помилка)'

    def get_object_author(self, obj):
        try:
            target = obj.content_object
            if target is None:
                return None
            author = getattr(target, 'author', None)
            return author.username if author else None
        except Exception:
            return None

    def get_object_slug(self, obj):
        """Для Post — повертає slug. Для Comment — None."""
        try:
            if obj.content_type.model == 'post':
                target = obj.content_object
                return getattr(target, 'slug', None) if target else None
            return None
        except Exception:
            return None

    def get_object_post_slug(self, obj):
        """Для Comment — повертає slug поста до якого належить коментар."""
        try:
            if obj.content_type.model == 'comment':
                target = obj.content_object
                if target and hasattr(target, 'post'):
                    return getattr(target.post, 'slug', None)
            return None
        except Exception:
            return None
