import json
from django.test import TestCase, Client

from .dao import PerevalDAO
from .models import Pereval, User, Coords


def sample_data(email='test@mail.ru', title='Тестовый перевал'):
    return {
        'beauty_title': 'пер. ',
        'title': title,
        'other_titles': 'Другое название',
        'connect': '',
        'add_time': '2021-09-22 13:18:13',
        'user': {
            'email': email,
            'fam': 'Пупкин',
            'name': 'Василий',
            'otc': 'Иванович',
            'phone': '+7 555 55 55',
        },
        'coords': {'latitude': '45.3842', 'longitude': '7.1525', 'height': '1200'},
        'level': {'winter': '', 'summer': '1А', 'autumn': '1А', 'spring': ''},
        'images': [{'data': 'img1base64', 'title': 'Седловина'}],
    }


class PerevalDAOTest(TestCase):
    """Тесты класса, отвечающего за работу с БД."""

    def test_add_pereval_creates_related_objects(self):
        data = sample_data()
        pereval_id = PerevalDAO.add_pereval(data)

        pereval = Pereval.objects.get(id=pereval_id)
        self.assertEqual(pereval.status, 'new')
        self.assertEqual(pereval.title, 'Тестовый перевал')
        self.assertEqual(pereval.user.email, 'test@mail.ru')
        self.assertEqual(pereval.coords.height, 1200)
        self.assertEqual(pereval.images.count(), 1)

        # повторное добавление с тем же email не создаёт нового пользователя
        second_data = sample_data(title='Второй перевал')
        PerevalDAO.add_pereval(second_data)
        self.assertEqual(User.objects.filter(email='test@mail.ru').count(), 1)

    def test_get_pereval_returns_none_if_missing(self):
        self.assertIsNone(PerevalDAO.get_pereval(9999))

    def test_update_pereval_success_when_status_new(self):
        pereval_id = PerevalDAO.add_pereval(sample_data())

        success, message = PerevalDAO.update_pereval(pereval_id, {'title': 'Обновлённое название'})

        self.assertTrue(success)
        pereval = Pereval.objects.get(id=pereval_id)
        self.assertEqual(pereval.title, 'Обновлённое название')

    def test_update_pereval_fails_when_status_not_new(self):
        pereval_id = PerevalDAO.add_pereval(sample_data())
        Pereval.objects.filter(id=pereval_id).update(status='accepted')

        success, message = PerevalDAO.update_pereval(pereval_id, {'title': 'Новое'})

        self.assertFalse(success)
        self.assertIn('accepted', message)

    def test_update_pereval_does_not_change_user_fields(self):
        pereval_id = PerevalDAO.add_pereval(sample_data())

        # даже если прислать другой email в user, он не должен применяться
        PerevalDAO.update_pereval(pereval_id, {'user': {'email': 'hacker@mail.ru'}})

        pereval = Pereval.objects.get(id=pereval_id)
        self.assertEqual(pereval.user.email, 'test@mail.ru')

    def test_get_perevals_by_email(self):
        PerevalDAO.add_pereval(sample_data(email='a@mail.ru', title='Перевал 1'))
        PerevalDAO.add_pereval(sample_data(email='a@mail.ru', title='Перевал 2'))
        PerevalDAO.add_pereval(sample_data(email='b@mail.ru', title='Перевал 3'))

        result = PerevalDAO.get_perevals_by_email('a@mail.ru')

        self.assertEqual(result.count(), 2)


class PerevalAPITest(TestCase):
    """Тесты REST API. Один тест может проверять цепочку из нескольких методов."""

    def setUp(self):
        self.client = Client()

    def test_submit_and_get_by_id(self):
        # создаём перевал через POST
        response = self.client.post(
            '/api/submitData/',
            data=json.dumps(sample_data()),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['status'], 200)
        pereval_id = body['id']
        self.assertIsNotNone(pereval_id)

        # проверяем, что запись действительно доступна через GET по id
        response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(response.status_code, 200)
        detail = response.json()
        self.assertEqual(detail['title'], 'Тестовый перевал')
        self.assertEqual(detail['status'], 'new')
        self.assertEqual(detail['user']['email'], 'test@mail.ru')

    def test_submit_data_missing_fields_returns_400(self):
        incomplete_data = {'title': 'Без пользователя и координат'}

        response = self.client.post(
            '/api/submitData/',
            data=json.dumps(incomplete_data),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 400)

    def test_patch_edit_success_when_new(self):
        create_response = self.client.post(
            '/api/submitData/',
            data=json.dumps(sample_data()),
            content_type='application/json',
        )
        pereval_id = create_response.json()['id']

        patch_response = self.client.patch(
            f'/api/submitData/{pereval_id}/',
            data=json.dumps({'title': 'Изменённое название'}),
            content_type='application/json',
        )

        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()['state'], 1)

        # убеждаемся, что изменение реально применилось
        get_response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(get_response.json()['title'], 'Изменённое название')

    def test_patch_edit_fails_when_status_not_new(self):
        create_response = self.client.post(
            '/api/submitData/',
            data=json.dumps(sample_data()),
            content_type='application/json',
        )
        pereval_id = create_response.json()['id']
        Pereval.objects.filter(id=pereval_id).update(status='pending')

        patch_response = self.client.patch(
            f'/api/submitData/{pereval_id}/',
            data=json.dumps({'title': 'Не должно примениться'}),
            content_type='application/json',
        )

        self.assertEqual(patch_response.json()['state'], 0)

    def test_list_by_email(self):
        self.client.post('/api/submitData/', data=json.dumps(sample_data(email='c@mail.ru', title='П1')), content_type='application/json')
        self.client.post('/api/submitData/', data=json.dumps(sample_data(email='c@mail.ru', title='П2')), content_type='application/json')

        response = self.client.get('/api/submitData/?user__email=c@mail.ru')

        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertEqual(len(results), 2)