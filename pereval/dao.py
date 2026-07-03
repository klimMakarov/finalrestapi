""" пользователь ищется по email, если не найден — создаётся;
 координаты и фото создаются всегда новые; статус жёстко ставится new"""


from django.db import transaction

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