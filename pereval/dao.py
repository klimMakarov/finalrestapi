""" пользователь ищется по email, если не найден — создаётся;
 координаты и фото создаются всегда новые; статус жёстко ставится new"""


from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


from .models import User, Coords, Image, Pereval, PerevalImage


class PerevalDAO:
    """Инкапсулирует работу с БД для сущности 'перевал'."""

    @staticmethod
    def get_or_create_user(user_data: dict) -> User:
        user, _ = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'fam': user_data.get('fam', ''),
                'name': user_data.get('name', ''),
                'otc': user_data.get('otc', ''),
                'phone': user_data.get('phone', ''),
            }
        )
        return user

    @staticmethod
    def create_coords(coords_data: dict) -> Coords:
        return Coords.objects.create(
            latitude=coords_data['latitude'],
            longitude=coords_data['longitude'],
            height=coords_data['height'],
        )

    @staticmethod
    def create_images(images_data: list) -> list:
        return [
            Image.objects.create(title=img.get('title', ''), data=img.get('data', ''))
            for img in images_data
        ]

    @classmethod
    def add_pereval(cls, data: dict) -> int:
        """Сохраняет перевал со всеми связанными объектами. Возвращает id."""
        with transaction.atomic():
            user = cls.get_or_create_user(data['user'])
            coords = cls.create_coords(data['coords'])
            level = data.get('level', {})

            pereval = Pereval.objects.create(
                beauty_title=data.get('beauty_title', ''),
                title=data['title'],
                other_titles=data.get('other_titles', ''),
                connect=data.get('connect', ''),
                add_time=data['add_time'],
                user=user,
                coords=coords,
                level_winter=level.get('winter', ''),
                level_summer=level.get('summer', ''),
                level_autumn=level.get('autumn', ''),
                level_spring=level.get('spring', ''),
                status='new',
            )

            for image in cls.create_images(data.get('images', [])):
                PerevalImage.objects.create(pereval=pereval, image=image)

            return pereval.id
        
    @staticmethod
    def get_pereval(pereval_id: int) -> Pereval | None:
        try:
            return (
                Pereval.objects
                .select_related('user', 'coords')
                .prefetch_related('images')
                .get(id=pereval_id)
            )
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_perevals_by_email(email: str):
        return (
            Pereval.objects
            .select_related('user', 'coords')
            .prefetch_related('images')
            .filter(user__email=email)
        )

    @classmethod
    def update_pereval(cls, pereval_id: int, data: dict) -> tuple[bool, str]:
        pereval = cls.get_pereval(pereval_id)

        if pereval is None:
            return False, 'Запись с указанным id не найдена'

        if pereval.status != 'new':
            return False, f'Редактирование запрещено: статус записи "{pereval.status}", а не "new"'

        with transaction.atomic():
            pereval.beauty_title = data.get('beauty_title', pereval.beauty_title)
            pereval.title = data.get('title', pereval.title)
            pereval.other_titles = data.get('other_titles', pereval.other_titles)
            pereval.connect = data.get('connect', pereval.connect)
            pereval.add_time = data.get('add_time', pereval.add_time)

            if 'coords' in data:
                coords_data = data['coords']
                pereval.coords.latitude = coords_data.get('latitude', pereval.coords.latitude)
                pereval.coords.longitude = coords_data.get('longitude', pereval.coords.longitude)
                pereval.coords.height = coords_data.get('height', pereval.coords.height)
                pereval.coords.save()

            if 'level' in data:
                level = data['level']
                pereval.level_winter = level.get('winter', pereval.level_winter)
                pereval.level_summer = level.get('summer', pereval.level_summer)
                pereval.level_autumn = level.get('autumn', pereval.level_autumn)
                pereval.level_spring = level.get('spring', pereval.level_spring)

            if 'images' in data:
                PerevalImage.objects.filter(pereval=pereval).delete()
                for image in cls.create_images(data['images']):
                    PerevalImage.objects.create(pereval=pereval, image=image)

            pereval.save()

        return True, 'Запись успешно обновлена'

    @staticmethod
    def serialize(pereval: Pereval) -> dict:
        return {
            'id': pereval.id,
            'status': pereval.status,
            'beauty_title': pereval.beauty_title,
            'title': pereval.title,
            'other_titles': pereval.other_titles,
            'connect': pereval.connect,
            'add_time': pereval.add_time,
            'user': {
                'email': pereval.user.email,
                'fam': pereval.user.fam,
                'name': pereval.user.name,
                'otc': pereval.user.otc,
                'phone': pereval.user.phone,
            },
            'coords': {
                'latitude': pereval.coords.latitude,
                'longitude': pereval.coords.longitude,
                'height': pereval.coords.height,
            },
            'level': {
                'winter': pereval.level_winter,
                'summer': pereval.level_summer,
                'autumn': pereval.level_autumn,
                'spring': pereval.level_spring,
            },
            'images': [
                {'id': img.id, 'title': img.title, 'data': img.data}
                for img in pereval.images.all()
            ],
        }