from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Product(models.Model):
    PRODUCT_TYPES = (
        ('tea', 'Чай'),
        ('coffee', 'Кофе'),
        ('accessory', 'Аксессуар'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class CoffeeComposition(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Aroma(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Additive(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CoffeeAttribute(models.Model):
    ROASTS = [
        ('light', 'Слабая'),
        ('medium', 'Средняя'),
        ('dark', 'Сильная')
    ]
    COFFEE_TYPES = [
        ('capsules', 'Капсулы'),
        ('ground', 'Молотый'),
        ('beans', 'В зернах')
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='coffee_attr')
    coffee_type = models.CharField(max_length=20, choices=COFFEE_TYPES)
    roast = models.CharField(max_length=20, choices=ROASTS)
    q_grading = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    compositions = models.ManyToManyField(CoffeeComposition)
    aromas = models.ManyToManyField(Aroma)
    additives = models.ManyToManyField(Additive)


class TeaCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'TeaCategories'

    def __str__(self):
        return self.name


class TeaAttribute(models.Model):
    TEA_TYPES = [
        ('bagged', 'Пакетированный'),
        ('loose', 'На развес')
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='tea_attr')
    tea_type = models.CharField(max_length=20, choices=TEA_TYPES)
    category = models.ForeignKey(TeaCategory, on_delete=models.CASCADE)
    aromas = models.ManyToManyField(Aroma)
    additives = models.ManyToManyField(Additive)


class AccessoryType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AccessoryAttribute(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='accessory_attr')
    accessory_type = models.ForeignKey(AccessoryType, on_delete=models.CASCADE)
    volume = models.DecimalField('volume (l)', max_digits=5, decimal_places=2, null=True, blank=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.PositiveIntegerField('weight (g)')
    pieces = models.PositiveIntegerField()
    text_description_of_count = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('product', 'text_description_of_count')
