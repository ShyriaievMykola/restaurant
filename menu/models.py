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
