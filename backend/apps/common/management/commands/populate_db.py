import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from apps.products.models import (
    Product, Variation, CoffeeAttribute, TeaAttribute, AccessoryAttribute,
    TeaCategory, AccessoryType, CoffeeComposition, Aroma, Additive
)
from apps.orders.models import Order, OrderItem
from apps.customer_collections.models import Cart, CartItem, Wishlist, WishlistItem

User = get_user_model()
fake = Faker('ru_RU')

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для интернет-магазина'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Очистить существующие данные перед заполнением')
        parser.add_argument('--users', type=int, default=10, help='Количество создаваемых пользователей')
        parser.add_argument('--products', type=int, default=20, help='Количество создаваемых товаров')
        parser.add_argument('--orders', type=int, default=15, help='Количество создаваемых заказов')

    def handle(self, *args, **options):
        self.stdout.write('Начинаем заполнение базы данными...')

        if options['clear']:
            self.clear_database()
            self.stdout.write('База данных очищена.')

        self.create_references()
        users = self.create_users(options['users'])
        products = self.create_products(options['products'])
        self.create_variations(products)
        carts = self.create_carts(users)
        orders = self.create_orders(users, products, options['orders'])
        self.create_wishlists(users, products)

        self.stdout.write(self.style.SUCCESS('Заполнение базы данных завершено успешно.'))

    def clear_database(self):
        # Очищаем основные таблицы, при этом суперпользователи не удаляются
        self.stdout.write('Очистка данных...')
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        WishlistItem.objects.all().delete()
        Wishlist.objects.all().delete()
        Variation.objects.all().delete()
        CoffeeAttribute.objects.all().delete()
        TeaAttribute.objects.all().delete()
        AccessoryAttribute.objects.all().delete()
        Product.objects.all().delete()

        # Справочники очищаем с осторожностью
        TeaCategory.objects.all().delete()
        AccessoryType.objects.all().delete()
        CoffeeComposition.objects.all().delete()
        Aroma.objects.all().delete()
        Additive.objects.all().delete()

        # Пользователей не чистим, чтобы не удалить суперпользователей
        # но можно удалить обычных пользователей, если нужно (опционально)

    def create_references(self):
        self.stdout.write('Создаем справочники...')

        tea_categories = [
            'Зеленый чай', 'Черный чай', 'Травяной чай', 'Пуэр', 'Белый чай', 'Улун'
        ]
        accessory_types = [
            'Чашки и кружки', 'Чайники', 'Кофемолки', 'Турки', 'Заварники'
        ]
        coffee_compositions = [
            '100% Арабика', 'Смесь', 'Эспрессо смесь'
        ]
        aromas = [
            'Цитрусовый', 'Шоколадный', 'Ванильный', 'Жасминовый', 'Ореховый'
        ]
        additives = [
            'Сахар', 'Молоко', 'Корица', 'Имбирь', 'Мед'
        ]

        for name in tea_categories:
            TeaCategory.objects.get_or_create(name=name)
        for name in accessory_types:
            AccessoryType.objects.get_or_create(name=name)
        for name in coffee_compositions:
            CoffeeComposition.objects.get_or_create(name=name)
        for name in aromas:
            Aroma.objects.get_or_create(name=name)
        for name in additives:
            Additive.objects.get_or_create(name=name)

    def create_users(self, count):
        self.stdout.write(f'Создаем {count} пользователей...')
        users = []
        existing_usernames = set(User.objects.values_list('username', flat=True))

        for i in range(count):
            username = None
            while True:
                username_candidate = fake.user_name() + str(random.randint(10, 99))
                if username_candidate not in existing_usernames:
                    username = username_candidate
                    existing_usernames.add(username_candidate)
                    break

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='test1234'
            )
            users.append(user)

        return users

    def create_products(self, count):
        self.stdout.write(f'Создаем {count} товаров...')
        products = []

        tea_category_ids = list(TeaCategory.objects.values_list('id', flat=True))
        accessory_type_ids = list(AccessoryType.objects.values_list('id', flat=True))
        coffee_compositions_ids = list(CoffeeComposition.objects.values_list('id', flat=True))
        aroma_ids = list(Aroma.objects.values_list('id', flat=True))
        additive_ids = list(Additive.objects.values_list('id', flat=True))

        PRODUCT_TYPES = ['tea', 'coffee', 'accessory']

        coffee_types = ['capsules', 'ground', 'beans']
        roast_types = ['light', 'medium', 'dark']

        tea_types = ['bagged', 'loose']

        for i in range(count):
            product_type = random.choice(PRODUCT_TYPES)
            name = ''
            product = None

            if product_type == 'coffee':
                name = random.choice(['Арабика', 'Бразильский', 'Эспрессо смесь']) + ' ' + fake.country()
                product = Product.objects.create(
                    name=name,
                    description=fake.text(max_nb_chars=150),
                    manufacturer=fake.company(),
                    country=fake.country(),
                    product_type='coffee',
                    available=True
                )
                coffee_attr = CoffeeAttribute.objects.create(
                    product=product,
                    coffee_type=random.choice(coffee_types),
                    roast=random.choice(roast_types),
                    q_grading=round(random.uniform(70, 90), 2)
                )

                # Добавляем связи ManyToMany
                compositions = CoffeeComposition.objects.order_by('?')[:random.randint(1, 2)]
                coffee_attr.compositions.set(compositions)
                aromas = Aroma.objects.order_by('?')[:random.randint(1, 3)]
                coffee_attr.aromas.set(aromas)
                additives = Additive.objects.order_by('?')[:random.randint(0, 2)]
                coffee_attr.additives.set(additives)

            elif product_type == 'tea':
                name = random.choice(['Зеленый жасминовый чай', 'Черный цейлонский чай', 'Пуэр']) + f' {fake.city()}'
                product = Product.objects.create(
                    name=name,
                    description=fake.text(max_nb_chars=150),
                    manufacturer=fake.company(),
                    country=fake.country(),
                    product_type='tea',
                    available=True
                )
                tea_attr = TeaAttribute.objects.create(
                    product=product,
                    tea_type=random.choice(tea_types),
                    category_id=random.choice(tea_category_ids)
                )
                aromas = Aroma.objects.order_by('?')[:random.randint(1, 3)]
                tea_attr.aromas.set(aromas)
                additives = Additive.objects.order_by('?')[:random.randint(0, 2)]
                tea_attr.additives.set(additives)

            else:  # accessory
                name = random.choice(['Керамическая турка', 'Стеклянный заварочный чайник', 'Френч-пресс'])
                product = Product.objects.create(
                    name=name,
                    description=fake.text(max_nb_chars=150),
                    manufacturer=fake.company(),
                    country=fake.country(),
                    product_type='accessory',
                    available=True
                )
                accessory_attr = AccessoryAttribute.objects.create(
                    product=product,
                    accessory_type_id=random.choice(accessory_type_ids),
                    volume=round(random.uniform(0.5, 2.0), 2)
                )

            products.append(product)

        return products

    def create_variations(self, products):
        self.stdout.write('Создаем вариации товаров...')

        for product in products:
            variations_count = random.randint(1, 3)

            weights = [100, 250, 500, 1000]
            pieces_options = [1, 5, 10, 20, 50]
            used_pairs = []

            for _ in range(variations_count):
                weight = random.choice(weights)
                pieces = random.choice([pieces for pieces in pieces_options if (pieces, weight) not in used_pairs])
                used_pairs.append((pieces, weight))
                text_description = f'{pieces} шт по {weight} гр'

                Variation.objects.create(
                    product=product,
                    price=round(random.uniform(100, 2000), 2),
                    weight=weight,
                    pieces=pieces,
                    text_description_of_count=text_description,
                    stock=random.randint(0, 100),
                    available=True
                )

    def create_carts(self, users):
        self.stdout.write('Создаем корзины для пользователей...')
        carts = []
        for user in users:
            cart = Cart.objects.create(user=user)
            # Добавляем случайные товары
            variations = Variation.objects.order_by('?')[:random.randint(1, 5)]
            for variation in variations:
                CartItem.objects.create(cart=cart, variation=variation, quantity=random.randint(1, 3))
            carts.append(cart)
        return carts

    def create_orders(self, users, products, count):
        self.stdout.write(f'Создаем {count} заказов...')
        orders = []
        status_choices = ['created', 'processing', 'shipped', 'delivered', 'canceled']

        for _ in range(count):
            user = random.choice(users)
            first_name = user.first_name
            last_name = user.last_name
            email = user.email
            phone = fake.phone_number()

            order = Order.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                paid=random.choice([True, False]),
                status=random.choice(status_choices)
            )

            # Добавляем позиции заказа
            order_items_count = random.randint(1, 5)
            variations = Variation.objects.order_by('?')[:order_items_count]
            for variation in variations:
                quantity = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    variation=variation,
                    price=variation.price,
                    quantity=quantity
                )

            orders.append(order)
        return orders

    def create_wishlists(self, users, products):
        self.stdout.write('Создаем списки желаний...')
        wishlists = []
        for user in users:
            wishlist = Wishlist.objects.create(user=user)
            fav_products = random.sample(products, min(len(products), random.randint(1, 5)))
            for product in fav_products:
                WishlistItem.objects.create(wishlist=wishlist, product=product)
            wishlists.append(wishlist)
        return wishlists
