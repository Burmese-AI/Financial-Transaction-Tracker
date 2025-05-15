from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from django.conf import settings
from transactions.models import Category

# Create your models here.
def current_month():
    return datetime.now().month

def current_year():
    return datetime.now().year


class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField(
        default=current_month, 
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    year = models.PositiveIntegerField(
        default=current_year
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'category', 'month', 'year')
        indexes = [
            models.Index(fields=['user', 'category', 'month', 'year'])
        ]

    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.month}/{self.year}): {self.amount}"


