import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=120)
	slug = models.SlugField(max_length=140, unique=True)
	description = models.TextField(blank=True)
	parent = models.ForeignKey(
		"self",
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name="children",
	)

	class Meta:
		ordering = ["name"]
		constraints = [
			models.UniqueConstraint(fields=["parent", "name"], name="uniq_category_name_per_parent")
		]

	def clean(self):
		super().clean()
		if self.parent_id and self.pk and self.parent_id == self.pk:
			raise ValidationError({"parent": "A category cannot be its own parent."})

		if self.parent and self.parent.parent_id:
			raise ValidationError({"parent": "Only two category levels are allowed."})

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class Tag(models.Model):
	name = models.CharField(max_length=80, unique=True)
	slug = models.SlugField(max_length=100, unique=True)

	class Meta:
		ordering = ["name"]

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class MenuItem(models.Model):
	name = models.CharField(max_length=140)
	slug = models.SlugField(max_length=160, unique=True)
	description = models.TextField(blank=True)
	price = models.DecimalField(
		max_digits=8,
		decimal_places=2,
		validators=[MinValueValidator(Decimal("0.01"))],
	)
	is_available = models.BooleanField(default=True)
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
	tags = models.ManyToManyField(Tag, blank=True, related_name="items")
	popularity_score = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]
		indexes = [
			models.Index(fields=["is_available"]),
			models.Index(fields=["price"]),
			models.Index(fields=["popularity_score"]),
			models.Index(fields=["created_at"]),
		]

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class Order(models.Model):
	order_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	first_name = models.CharField(max_length=120)
	last_name = models.CharField(max_length=120)
	email = models.EmailField(max_length=254)
	phone = models.CharField(max_length=40)
	address = models.TextField()
	status = models.CharField(max_length=30, default="pending")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Order {self.order_uuid}"

	@property
	def total_price(self):
		return sum(item.total_price for item in self.items.all())

	@property
	def total_quantity(self):
		return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
	price = models.DecimalField(max_digits=8, decimal_places=2)
	quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

	class Meta:
		ordering = ["id"]

	def save(self, *args, **kwargs):
		if not self.price:
			self.price = self.menu_item.price
		return super().save(*args, **kwargs)

	@property
	def total_price(self):
		return self.price * self.quantity

	def __str__(self):
		return f"{self.quantity} × {self.menu_item.name}"
