from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        wait = exc.wait
        data = {
            'error': 'rate_limit_exceeded',
            'message': exc.detail if exc.detail != 'Request was throttled.' else 'Забагато запитів',
            'retry_after': int(wait) if wait else None,
        }
        return Response(data, status=429)

    return response
