from django.db import models

# Create your models here.

class ProductCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'

class ProductSubcategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название подкатегории')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='subcategories', verbose_name='Категория')
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    class Meta:
        verbose_name = 'Подкатегория товара'
        verbose_name_plural = 'Подкатегории товаров'

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(upload_to='products/', verbose_name='Фото')
    stock = models.PositiveIntegerField(verbose_name='Остаток')
    subcategory = models.ForeignKey(ProductSubcategory, on_delete=models.CASCADE, related_name='products', verbose_name='Подкатегория')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class Client(models.Model):
    telegram_id = models.CharField(max_length=100, unique=True, verbose_name='Telegram ID')
    username = models.CharField(max_length=100, verbose_name='Имя пользователя')
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders', verbose_name='Клиент')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    delivery_address = models.TextField(verbose_name='Адрес доставки')
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders', verbose_name='Товары')
    
    def __str__(self):
        return f"Заказ {self.id} от {self.client.username}"
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

class CartItem(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cart_items', verbose_name='Клиент')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} в корзине {self.client.username}"
    
    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
