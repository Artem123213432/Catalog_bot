from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    image_url: str
    subcategory_id: int

@dataclass
class Subcategory:
    id: int
    name: str
    category_id: int
    products: List[Product]

@dataclass
class Category:
    id: int
    name: str
    subcategories: List[Subcategory]


CATEGORIES = [
    Category(
        id=1,
        name="Электроника",
        subcategories=[
            Subcategory(
                id=1,
                name="Смартфоны",
                category_id=1,
                products=[
                    Product(
                        id=1,
                        name="iPhone 16",
                        description="Новейший смартфон от Apple",
                        price=70000.00,
                        image_url="https://avatars.mds.yandex.net/get-mpic/12363834/2a0000018e9ebc9f7a5e4a239d4e92a6bfe9/orig",
                        subcategory_id=1
                    )
                ]
            ),
            Subcategory(
                id=2,
                name="Ноутбуки",
                category_id=1,
                products=[
                    Product(
                        id=3,
                        name="MacBook Pro",
                        description="Мощный ноутбук для профессионалов",
                        price=100000.00,
                        image_url="https://p0.zoon.ru/preview/mveWbQUTM5jbgQHWJ9v85Q/2400x1500x75/1/4/9/original_633d9695e8989e426b048d70_6343df115b5091.14041840.jpg",
                        subcategory_id=2
                    )
                ]
            )
        ]
    ),
    Category(
        id=2,
        name="Одежда",
        subcategories=[
            Subcategory(
                id=3,
                name="Мужская одежда",
                category_id=2,
                products=[
                    Product(
                        id=4,
                        name="Джинсы",
                        description="Классические джинсы",
                        price=5000.00,
                        image_url="https://odezhda.guru/wp-content/uploads/2018/08/Praktichnyj-denim.jpg",
                        subcategory_id=3
                    )
                ]
            )
        ]
    )
] 