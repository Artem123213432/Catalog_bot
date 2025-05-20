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

# Пример данных (в реальном приложении данные будут храниться в базе данных)
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
                        name="iPhone 13",
                        description="Новейший смартфон от Apple",
                        price=799.99,
                        image_url="https://avatars.mds.yandex.net/get-mpic/12363834/2a0000018e9ebc9f7a5e4a239d4e92a6bfe9/orig",
                        subcategory_id=1
                    ),
                    Product(
                        id=2,
                        name="Samsung Galaxy S21",
                        description="Флагманский смартфон от Samsung",
                        price=699.99,
                        image_url="https://example.com/s21.jpg",
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
                        price=1299.99,
                        image_url="https://example.com/macbook.jpg",
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
                        price=49.99,
                        image_url="https://example.com/jeans.jpg",
                        subcategory_id=3
                    )
                ]
            )
        ]
    )
] 