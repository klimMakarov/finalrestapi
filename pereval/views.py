from django.shortcuts import render


import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .dao import PerevalDAO

REQUIRED_TOP_FIELDS = ['title', 'add_time', 'user', 'coords']
REQUIRED_USER_FIELDS = ['email', 'fam', 'name']
REQUIRED_COORDS_FIELDS = ['latitude', 'longitude', 'height']


def _validate(data: dict) -> str | None:
    for field in REQUIRED_TOP_FIELDS:
        if not data.get(field):
            return f'Не заполнено обязательное поле: {field}'

    user = data.get('user', {})
    for field in REQUIRED_USER_FIELDS:
        if not user.get(field):
            return f'Не заполнено обязательное поле: user.{field}'

    coords = data.get('coords', {})
    for field in REQUIRED_COORDS_FIELDS:
        if coords.get(field) in (None, ''):
            return f'Не заполнено обязательное поле: coords.{field}'

    return None


@csrf_exempt
@require_http_methods(['POST'])
def submit_data(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 400, 'message': 'Некорректный JSON', 'id': None}, status=400)

    error = _validate(data)
    if error:
        return JsonResponse({'status': 400, 'message': error, 'id': None}, status=400)

    try:
        new_id = PerevalDAO.add_pereval(data)
    except Exception as e:
        return JsonResponse(
            {'status': 500, 'message': f'Ошибка подключения к базе данных: {e}', 'id': None},
            status=500,
        )

    return JsonResponse({'status': 200, 'message': None, 'id': new_id}, status=200)