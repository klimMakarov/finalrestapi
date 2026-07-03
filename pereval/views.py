import json

from django.shortcuts import render
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
@require_http_methods(['GET', 'POST'])
def submit_data(request):
    if request.method == 'POST':
        return _create_pereval(request)
    return _list_perevals(request)


def _create_pereval(request):
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


def _list_perevals(request):
    email = request.GET.get('user__email')
    if not email:
        return JsonResponse({'status': 400, 'message': 'Не указан параметр user__email'}, status=400)

    perevals = PerevalDAO.get_perevals_by_email(email)
    result = [PerevalDAO.serialize(p) for p in perevals]
    return JsonResponse(result, safe=False, status=200)


@csrf_exempt
@require_http_methods(['GET', 'PATCH'])
def pereval_detail(request, pereval_id):
    if request.method == 'GET':
        return _get_pereval(pereval_id)
    return _update_pereval(request, pereval_id)


def _get_pereval(pereval_id):
    pereval = PerevalDAO.get_pereval(pereval_id)
    if pereval is None:
        return JsonResponse({'message': 'Запись не найдена'}, status=404)
    return JsonResponse(PerevalDAO.serialize(pereval), status=200)


def _update_pereval(request, pereval_id):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'state': 0, 'message': 'Некорректный JSON'}, status=400)

    try:
        success, message = PerevalDAO.update_pereval(pereval_id, data)
    except Exception as e:
        return JsonResponse({'state': 0, 'message': f'Ошибка при обновлении: {e}'}, status=500)

    return JsonResponse({'state': 1 if success else 0, 'message': message}, status=200)