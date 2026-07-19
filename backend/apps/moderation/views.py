import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Report
from .serializers import ReportCreateSerializer, ReportAdminSerializer

logger = logging.getLogger('apps.moderation')


class IsStaff(permissions.BasePermission):
    """Тільки is_staff юзери"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class ReportPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ── Юзерські ендпоінти ────────────────────────────────────────

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_report(request):
    """
    POST /api/v1/moderation/report/
    Юзер подає скаргу на пост або коментар.

    Body: { content_type_name: 'post'|'comment', object_id: 123,
            reason: 'spam'|'hate'|'misleading'|'nsfw'|'other',
            comment: '...' (необовʼязково) }
    """
    serializer = ReportCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)

    try:
        report = serializer.save()
        logger.info(
            'New report #%s: %s on %s#%s by %s',
            report.pk, report.reason,
            report.content_type.model, report.object_id,
            request.user.username
        )
        return Response(
            {'message': 'Скаргу прийнято. Ми розглянемо її найближчим часом.'},
            status=status.HTTP_201_CREATED
        )
    except Exception:
        # unique_together — юзер вже скаржився на цей обʼєкт
        return Response(
            {'message': 'Ви вже подавали скаргу на цей матеріал.'},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_reported(request):
    """
    GET /api/v1/moderation/check/?content_type=post&object_id=123
    Чи поточний юзер вже репортив цей обʼєкт.
    """
    from django.contrib.contenttypes.models import ContentType

    ct_name = request.query_params.get('content_type')
    object_id = request.query_params.get('object_id')

    if not ct_name or not object_id:
        return Response({'reported': False})

    try:
        ct = ContentType.objects.get(model=ct_name)
        reported = Report.objects.filter(
            reporter=request.user,
            content_type=ct,
            object_id=object_id
        ).exists()
        return Response({'reported': reported})
    except ContentType.DoesNotExist:
        return Response({'reported': False})


# ── Адмін ендпоінти ───────────────────────────────────────────

class AdminReportQueueView(generics.ListAPIView):
    """
    GET /api/v1/moderation/admin/queue/
    Черга репортів для адміна. Підтримує фільтр ?status=pending|resolved|rejected
    """
    serializer_class = ReportAdminSerializer
    permission_classes = [IsStaff]
    pagination_class = ReportPagination

    def get_queryset(self):
        qs = Report.objects.select_related(
            'reporter', 'reviewed_by', 'content_type'
        )
        status_filter = self.request.query_params.get('status', 'pending')
        if status_filter in ('pending', 'resolved', 'rejected'):
            qs = qs.filter(status=status_filter)
        return qs


@api_view(['POST'])
@permission_classes([IsStaff])
def resolve_report(request, report_id):
    """
    POST /api/v1/moderation/admin/<report_id>/resolve/
    Адмін підтверджує скаргу — видаляє контент і закриває всі репорти на нього.

    Body: { admin_note: '...' (необовʼязково) }
    """
    report = get_object_or_404(Report, pk=report_id)

    if report.status != Report.Status.PENDING:
        return Response(
            {'error': 'Репорт вже оброблено'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Видаляємо сам обʼєкт
    target = report.content_object
    target_desc = f'{report.content_type.model}#{report.object_id}'

    if target is None:
        return Response(
            {'error': 'Обʼєкт вже видалено'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        # Для Comment — soft delete (is_active=False)
        if report.content_type.model == 'comment':
            target.is_active = False
            target.save()
        else:
            # Для Post — справжнє видалення (або теж soft: status='deleted')
            target.delete()

        logger.info(
            'Admin %s resolved report #%s: deleted %s',
            request.user.username, report_id, target_desc
        )
    except Exception as e:
        logger.error('Error deleting %s: %s', target_desc, e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Закриваємо ВСІ репорти на цей обʼєкт (не тільки поточний)
    Report.objects.filter(
        content_type=report.content_type,
        object_id=report.object_id,
        status=Report.Status.PENDING
    ).update(
        status=Report.Status.RESOLVED,
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
        admin_note=request.data.get(
            'admin_note', f'Видалено адміном {request.user.username}')
    )

    return Response({'message': f'{target_desc} видалено, всі скарги закрито'})


@api_view(['POST'])
@permission_classes([IsStaff])
def reject_report(request, report_id):
    """
    POST /api/v1/moderation/admin/<report_id>/reject/
    Адмін відхиляє скаргу — контент залишається, репорт закривається.
    """
    report = get_object_or_404(Report, pk=report_id)

    if report.status != Report.Status.PENDING:
        return Response(
            {'error': 'Репорт вже оброблено'},
            status=status.HTTP_400_BAD_REQUEST
        )

    report.status = Report.Status.REJECTED
    report.reviewed_by = request.user
    report.reviewed_at = timezone.now()
    report.admin_note = request.data.get('admin_note', '')
    report.save()

    logger.info(
        'Admin %s rejected report #%s',
        request.user.username, report_id
    )

    return Response({'message': 'Скаргу відхилено, контент залишено'})


@api_view(['GET'])
@permission_classes([IsStaff])
def admin_stats(request):
    """
    GET /api/v1/moderation/admin/stats/
    Швидка статистика для бейджу в профілі адміна.
    """
    pending_count = Report.objects.filter(status=Report.Status.PENDING).count()
    return Response({
        'pending_count': pending_count,
    })
