import random
import requests
import bs4
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from apps.products.models import (
    Product, Variation, CoffeeAttribute, TeaAttribute, AccessoryAttribute,
    TeaCategory, AccessoryType, Aroma, Additive, Country, Manufacturer
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
        parser.add_argument('--countries', type=int, default=20, help='Количество создаваемых стран')
        parser.add_argument('--manufacturers', type=int, default=20, help='Количество создаваемых производителей')

    def handle(self, *args, **options):
        self.stdout.write('Начинаем заполнение базы данными...')

        if options['clear']:
            self.clear_database()
            self.stdout.write('База данных очищена.')

        self.create_references(options['countries'], options['manufacturers'])
        users = self.create_users(options['users'])
        products = self.create_products(options['products'])
        self.create_variations(products)
        carts = self.create_carts(users)
        orders = self.create_orders(users, products, options['orders'])
        self.create_wishlists(users, products)

        self.stdout.write(self.style.SUCCESS('Заполнение базы данных завершено успешно.'))

    def get_tea_names_generator(self):
        words = {
            'masculine': {
                'adjectives': [
                    'Нефритовый', 'Жемчужный', 'Лунный', 'Персиковый', 'Серебристый', 'Фиолетовый', 'Лазурный',
                    'Небесный', 'Радужный', 'Опаловый',
                    'Весенний', 'Летний', 'Осенний', 'Зимний', 'Утренний', 'Вечерний', 'Полуденный', 'Рассветный',
                    'Закатный', 'Сумеречный',
                    'Тихий', 'Спокойный', 'Мирный', 'Безмятежный', 'Умиротворенный', 'Созерцательный', 'Медитативный',
                    'Философский', 'Мудрый'
                ],
                'nouns': [
                    'Бриз', 'Ручей', 'Листопад', 'Дракон', 'Журавль', 'Лотос', 'Бамбук', 'Ветер', 'Поток', 'Источник',
                    'Сад', 'Храм', 'Монастырь', 'Павильон', 'Дворец', 'Мост', 'Холм', 'Пик', 'Склон', 'Обрыв',
                    'Путь', 'Маршрут', 'Переход', 'Проход', 'Коридор', 'Тоннель', 'Мир', 'Космос', 'Эфир'
                ]
            },
            'feminine': {
                'adjectives': [
                    'Нефритовая', 'Жемчужная', 'Лунная', 'Персиковая', 'Серебристая', 'Фиолетовая', 'Лазурная',
                    'Небесная', 'Радужная', 'Опаловая',
                    'Весенняя', 'Летняя', 'Осенняя', 'Зимняя', 'Утренняя', 'Вечерняя', 'Полуденная', 'Рассветная',
                    'Закатная', 'Сумеречная',
                    'Тихая', 'Спокойная', 'Мирная', 'Безмятежная', 'Умиротворенная', 'Созерцательная', 'Медитативная',
                    'Философская', 'Мудрая'
                ],
                'nouns': [
                    'Гармония', 'Роса', 'Сакура', 'Ива', 'Мудрость', 'Элегантность', 'Традиция', 'Церемония',
                    'Медитация', 'Тишина',
                    'Грация', 'Пластика', 'Красота', 'Нежность', 'Утонченность', 'Изысканность', 'Деликатность',
                    'Хрупкость', 'Воздушность', 'Легкость',
                    'Душа', 'Суть', 'Основа', 'Глубина', 'Высота', 'Ширь', 'Даль', 'Бездна', 'Пропасть'
                ]
            },
            'neuter': {
                'adjectives': [
                    'Нефритовое', 'Жемчужное', 'Лунное', 'Персиковое', 'Серебристое', 'Фиолетовое', 'Лазурное',
                    'Небесное', 'Радужное', 'Опаловое',
                    'Весеннее', 'Летнее', 'Осеннее', 'Зимнее', 'Утреннее', 'Вечернее', 'Полуденное', 'Рассветное',
                    'Закатное', 'Сумеречное',
                    'Тихое', 'Спокойное', 'Мирное', 'Безмятежное', 'Умиротворенное', 'Созерцательное', 'Медитативное',
                    'Философское', 'Мудрое'
                ],
                'nouns': [
                    'Спокойствие', 'Умиротворение', 'Блаженство', 'Цветение', 'Просветление', 'Созерцание', 'Изящество',
                    'Равновесие', 'Единство', 'Слияние',
                    'Дыхание', 'Сердцебиение', 'Молчание', 'Безмолвие', 'Затишье', 'Покой', 'Отдохновение',
                    'Расслабление', 'Освобождение', 'Очищение'
                ]
            },
            'single': [
                'Медитация', 'Дракон', 'Журавль', 'Гармония', 'Сакура', 'Лотос', 'Мудрость', 'Церемония', 'Традиция',
                'Элегантность',
                'Спокойствие', 'Блаженство', 'Просветление', 'Созерцание', 'Изящество', 'Равновесие', 'Единство',
                'Безмятежность'
            ]
        }

        patterns = [
            lambda: f"{random.choice(words['masculine']['adjectives'])} {random.choice(words['masculine']['nouns'])}",
            lambda: f"{random.choice(words['feminine']['adjectives'])} {random.choice(words['feminine']['nouns'])}",
            lambda: f"{random.choice(words['neuter']['adjectives'])} {random.choice(words['neuter']['nouns'])}",
            lambda: random.choice(words['single'])
        ]

        return lambda: random.choice(patterns)()

    def get_coffee_names_generator(self):
        words = {
            'masculine': {
                'adjectives': [
                    'Золотой', 'Серебряный', 'Изумрудный', 'Алый', 'Янтарный', 'Рубиновый', 'Сапфировый', 'Медный',
                    'Бронзовый', 'Багровый',
                    'Горный', 'Океанский', 'Северный', 'Тропический', 'Лесной', 'Южный', 'Восточный', 'Западный',
                    'Полярный', 'Степной',
                    'Королевский', 'Императорский', 'Благородный', 'Величественный', 'Торжественный', 'Священный',
                    'Божественный', 'Мистический'
                ],
                'nouns': [
                    'Рассвет', 'Закат', 'Туман', 'Огонь', 'Ветер', 'Гром', 'Шторм', 'Ураган', 'Вихрь', 'Смерч',
                    'Феникс', 'Дракон', 'Титан', 'Пегас', 'Грифон', 'Минотавр', 'Кентавр', 'Циклоп', 'Атлант', 'Гигант',
                    'Триумф', 'Пик', 'Восход', 'Зенит', 'Апогей', 'Кульминация', 'Финал', 'Эпилог', 'Акцент', 'Штрих'
                ]
            },
            'feminine': {
                'adjectives': [
                    'Золотая', 'Серебряная', 'Изумрудная', 'Алая', 'Янтарная', 'Рубиновая', 'Сапфировая', 'Медная',
                    'Бронзовая', 'Багровая',
                    'Горная', 'Океанская', 'Северная', 'Тропическая', 'Лесная', 'Южная', 'Восточная', 'Западная',
                    'Полярная', 'Степная',
                    'Королевская', 'Императорская', 'Благородная', 'Величественная', 'Торжественная', 'Священная',
                    'Божественная', 'Мистическая'
                ],
                'nouns': [
                    'Страсть', 'Магия', 'Легенда', 'Мечта', 'Тайна', 'Загадка', 'Мистерия', 'Интрига', 'Сага', 'Эпопея',
                    'Звезда', 'Луна', 'Комета', 'Галактика', 'Вселенная', 'Бесконечность', 'Вечность', 'Судьба',
                    'Удача', 'Фортуна',
                    'Элегантность', 'Слава', 'Победа', 'Честь', 'Доблесть', 'Отвага', 'Смелость', 'Сила', 'Мощь',
                    'Энергия'
                ]
            },
            'neuter': {
                'adjectives': [
                    'Золотое', 'Серебряное', 'Изумрудное', 'Алое', 'Янтарное', 'Рубиновое', 'Сапфировое', 'Медное',
                    'Бронзовое', 'Багровое',
                    'Горное', 'Океанское', 'Северное', 'Тропическое', 'Лесное', 'Южное', 'Восточное', 'Западное',
                    'Полярное', 'Степное',
                    'Королевское', 'Императорское', 'Благородное', 'Величественное', 'Торжественное', 'Священное',
                    'Божественное', 'Мистическое'
                ],
                'nouns': [
                    'Чудо', 'Величие', 'Благородство', 'Откровение', 'Вдохновение', 'Совершенство', 'Наслаждение',
                    'Очарование', 'Блаженство', 'Восхищение',
                    'Сияние', 'Свечение', 'Мерцание', 'Искрение', 'Пламя', 'Пылание', 'Горение', 'Дыхание', 'Биение',
                    'Движение'
                ]
            },
            'single': [
                'Магия', 'Феникс', 'Дракон', 'Мечта', 'Чудо', 'Триумф', 'Легенда', 'Тайна', 'Страсть', 'Величие',
                'Титан', 'Пегас', 'Грифон', 'Звезда', 'Комета', 'Вихрь', 'Гром', 'Шторм', 'Рассвет', 'Закат',
                'Элегантность', 'Совершенство', 'Вдохновение', 'Откровение', 'Блаженство', 'Очарование', 'Восхищение'
            ]
        }

        patterns = [
            lambda: f"{random.choice(words['masculine']['adjectives'])} {random.choice(words['masculine']['nouns'])}",
            lambda: f"{random.choice(words['feminine']['adjectives'])} {random.choice(words['feminine']['nouns'])}",
            lambda: f"{random.choice(words['neuter']['adjectives'])} {random.choice(words['neuter']['nouns'])}",
            lambda: random.choice(words['single'])
        ]

        return lambda: random.choice(patterns)()

    def get_accessories_names_generator(self):
        words = {
            'masculine': {
                'adjectives': [
                    'Классический', 'Винтажный', 'Современный', 'Минималистичный', 'Элегантный', 'Изысканный',
                    'Роскошный', 'Утонченный', 'Благородный', 'Стильный',
                    'Керамический', 'Стальной', 'Медный', 'Хрустальный', 'Фарфоровый', 'Стеклянный', 'Мраморный',
                    'Гранитный', 'Деревянный', 'Кожаный',
                    'Округлый', 'Плавный', 'Граненый', 'Угловатый', 'Обтекаемый', 'Рельефный', 'Гладкий', 'Текстурный',
                    'Матовый', 'Глянцевый'
                ],
                'nouns': [
                    'Мастер', 'Дизайн', 'Премиум', 'Стиль', 'Силуэт', 'Контур', 'Образ', 'Комфорт', 'Престиж', 'Шарм',
                    'Архитектор', 'Художник', 'Скульптор', 'Творец', 'Создатель', 'Виртуоз', 'Гений', 'Талант',
                    'Профессионал', 'Эксперт',
                    'Акцент', 'Штрих', 'Мазок', 'Росчерк', 'Эскиз', 'Набросок', 'Этюд', 'Портрет', 'Пейзаж'
                ]
            },
            'feminine': {
                'adjectives': [
                    'Классическая', 'Винтажная', 'Современная', 'Минималистичная', 'Элегантная', 'Изысканная',
                    'Роскошная', 'Утонченная', 'Благородная', 'Стильная',
                    'Керамическая', 'Стальная', 'Медная', 'Хрустальная', 'Фарфоровая', 'Стеклянная', 'Мраморная',
                    'Гранитная', 'Деревянная', 'Кожаная',
                    'Округлая', 'Плавная', 'Граненая', 'Угловатая', 'Обтекаемая', 'Рельефная', 'Гладкая', 'Текстурная',
                    'Матовая', 'Глянцевая'
                ],
                'nouns': [
                    'Студия', 'Коллекция', 'Гармония', 'Элегантность', 'Линия', 'Форма', 'Композиция', 'Симфония',
                    'Рапсодия', 'Фантазия',
                    'Галерея', 'Выставка', 'Экспозиция', 'Презентация', 'Демонстрация', 'Иллюстрация', 'Интерпретация',
                    'Версия', 'Вариация', 'Модификация',
                    'Палитра', 'Гамма', 'Тональность', 'Окраска', 'Фактура', 'Текстура', 'Поверхность', 'Плоскость'
                ]
            },
            'neuter': {
                'adjectives': [
                    'Классическое', 'Винтажное', 'Современное', 'Минималистичное', 'Элегантное', 'Изысканное',
                    'Роскошное', 'Утонченное', 'Благородное', 'Стильное',
                    'Керамическое', 'Стальное', 'Медное', 'Хрустальное', 'Фарфоровое', 'Стеклянное', 'Мраморное',
                    'Гранитное', 'Деревянное', 'Кожаное',
                    'Округлое', 'Плавное', 'Граненое', 'Угловатое', 'Обтекаемое', 'Рельефное', 'Гладкое', 'Текстурное',
                    'Матовое', 'Глянцевое'
                ],
                'nouns': [
                    'Совершенство', 'Величие', 'Мастерство', 'Искусство', 'Творчество', 'Воплощение', 'Олицетворение',
                    'Выражение', 'Отражение', 'Воспроизведение',
                    'Решение', 'Исполнение', 'Воплощение', 'Создание', 'Формирование', 'Моделирование',
                    'Проектирование', 'Планирование'
                ]
            },
            'single': [
                'Премиум', 'Мастер', 'Студия', 'Элегантность', 'Дизайн', 'Гармония', 'Престиж', 'Комфорт',
                'Совершенство', 'Величие',
                'Классика', 'Стиль', 'Форма', 'Линия', 'Искусство', 'Творчество', 'Мастерство', 'Шарм'
            ]
        }

        patterns = [
            lambda: f"{random.choice(words['masculine']['adjectives'])} {random.choice(words['masculine']['nouns'])}",
            lambda: f"{random.choice(words['feminine']['adjectives'])} {random.choice(words['feminine']['nouns'])}",
            lambda: f"{random.choice(words['neuter']['adjectives'])} {random.choice(words['neuter']['nouns'])}",
            lambda: random.choice(words['single'])
        ]

        return lambda: random.choice(patterns)()

    def clear_database(self):
        # Основные таблицы
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

        # Справочники
        TeaCategory.objects.all().delete()
        AccessoryType.objects.all().delete()
        Aroma.objects.all().delete()
        Additive.objects.all().delete()
        Country.objects.all().delete()
        Manufacturer.objects.all().delete()

    def create_references(self, countries_count=20, manufacturers_count=20):
        self.stdout.write('Создаем справочники...')

        tea_categories = [
            'Зеленый чай', 'Черный чай', 'Травяной чай', 'Пуэр', 'Белый чай', 'Улун'
        ]
        accessory_types = [
            'Чашки и кружки', 'Чайники', 'Кофемолки', 'Турки', 'Заварники'
        ]
        additives = [
            'Корица молотая', 'Кардамон зерна', 'Имбирь сушеный', 'Ваниль стручки',
            'Гвоздика бутоны', 'Мускатный орех молотый', 'Анис звездчатый', 'Фенхель семена',
            'Цедра апельсина сушеная', 'Цедра лимона сушеная', 'Лепестки розы сушеные', 'Жасмин цветки',
            'Лаванда сушеная', 'Мята сушеная', 'Мелисса листья', 'Какао бобы дробленые',
            'Миндаль лепестки', 'Кокосовая стружка', 'Яблоко сушеное кусочки', 'Вишня сушеная'
        ]
        aromas = [
            'Шоколадный', 'Ванильный', 'Карамельный', 'Ореховый', 'Цитрусовый',
            'Цветочный', 'Фруктовый', 'Пряный', 'Медовый', 'Древесный',
            'Землистый', 'Травяной', 'Мятный', 'Лавандовый', 'Розовый',
            'Жасминовый', 'Бергамотовый', 'Малиновый', 'Яблочный', 'Персиковый'
        ]
        countries = [fake.country() for _ in range(countries_count)]
        manufacturers = [fake.company() for _ in range(manufacturers_count)]

        for name in tea_categories:
            TeaCategory.objects.get_or_create(name=name)
        for name in accessory_types:
            AccessoryType.objects.get_or_create(name=name)
        for name in aromas:
            Aroma.objects.get_or_create(name=name)
        for name in additives:
            Additive.objects.get_or_create(name=name)
        for name in countries:
            Country.objects.get_or_create(name=name)
        for name in manufacturers:
            Manufacturer.objects.get_or_create(name=name)

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
        # country_ids = list(Country.objects.values_list('id', flat=True))
        # manufacturer_ids = list(Manufacturer.objects.values_list('id', flat=True))
        # aroma_ids = list(Aroma.objects.values_list('id', flat=True))
        # additive_ids = list(Additive.objects.values_list('id', flat=True))

        PRODUCT_TYPES = ['tea', 'coffee', 'accessory']

        coffee_types = ['capsules', 'ground', 'beans']
        roast_types = ['light', 'medium', 'dark']
        coffee_names_generator = self.get_coffee_names_generator()

        tea_types = ['bagged', 'loose']
        tea_names_generator = self.get_tea_names_generator()

        accessories_names_generator = self.get_accessories_names_generator()

        for i in range(count):
            product_type = random.choice(PRODUCT_TYPES)
            name = tea_names_generator() if product_type == 'tea' else (
                coffee_names_generator() if product_type == 'coffee' else accessories_names_generator())
            product = Product.objects.create(
                name=name,
                description=fake.text(max_nb_chars=150),
                product_type=product_type,
                available=True,
                manufacturer=Manufacturer.objects.order_by('?').first(),
                country=Country.objects.order_by('?').first(),
                region=fake.city() if random.choice([True, False, False]) else None
            )

            if product_type == 'coffee':
                Arabica_percentage = random.randint(0, 100)
                Robusta_percentage = random.randint(0, 100 - Arabica_percentage)
                Liberica_percentage = 100 - Arabica_percentage - Robusta_percentage

                coffee_attr = CoffeeAttribute.objects.create(
                    product=product,
                    coffee_type=random.choice(coffee_types),
                    roast=random.choice(roast_types),
                    q_grading=round(random.uniform(70, 90), 2),
                    arabica_percent=Arabica_percentage,
                    robusta_percent=Robusta_percentage,
                    liberica_percent=Liberica_percentage,
                )

                # Добавляем связи ManyToMany
                aromas = Aroma.objects.order_by('?')[:random.randint(1, 3)]
                coffee_attr.aromas.set(aromas)
                additives = Additive.objects.order_by('?')[:random.randint(0, 2)]
                coffee_attr.additives.set(additives)

                coffee_attr.arabica_percentage = Arabica_percentage
                coffee_attr.robusta_percentage = Robusta_percentage
                coffee_attr.liberica_percentage = Liberica_percentage

            elif product_type == 'tea':
                tea_attr = TeaAttribute.objects.create(
                    product=product,
                    tea_type=random.choice(tea_types),
                    category_id=random.choice(tea_category_ids)
                )
                aromas = Aroma.objects.order_by('?')[:random.randint(1, 3)]
                tea_attr.aromas.set(aromas)
                additives = Additive.objects.order_by('?')[:random.randint(0, 2)]
                tea_attr.additives.set(additives)

            else:
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
