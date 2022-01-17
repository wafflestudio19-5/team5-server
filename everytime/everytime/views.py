from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404

from rest_framework import exceptions, status
from rest_framework.views import set_rollback
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

def ping(request):
    return HttpResponse('pong')

# 에러 로그 쌓으려고 만들었는데 아직 완성 못 함
def exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'detail': exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return Response({
        'detatil': '서버 에러입니다. 서버 관리자에게 문의 바랍니다.',
        'code': 'E000'
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

