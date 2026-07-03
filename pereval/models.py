from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    fam = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    otc = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.fam} {self.name}'


class Coords(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.IntegerField()

    class Meta:
        db_table = 'coords'


class Image(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    data = models.TextField()  # base64 содержимого фото
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pereval_images'


class Pereval(models.Model):
    STATUS_CHOICES = [
        ('new', 'new'),
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
    ]

    beauty_title = models.CharField(max_length=255, blank=True, default='')
    title = models.CharField(max_length=255)
    other_titles = models.CharField(max_length=255, blank=True, default='')
    connect = models.CharField(max_length=255, blank=True, default='')
    add_time = models.DateTimeField()
    date_added = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='perevals')
    coords = models.OneToOneField(Coords, on_delete=models.CASCADE)

    level_winter = models.CharField(max_length=10, blank=True, default='')
    level_summer = models.CharField(max_length=10, blank=True, default='')
    level_autumn = models.CharField(max_length=10, blank=True, default='')
    level_spring = models.CharField(max_length=10, blank=True, default='')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    images = models.ManyToManyField(Image, through='PerevalImage', related_name='perevals')

    class Meta:
        db_table = 'pereval_added'


class PerevalImage(models.Model):
    pereval = models.ForeignKey(Pereval, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)

    class Meta:
        db_table = 'pereval_images_link'