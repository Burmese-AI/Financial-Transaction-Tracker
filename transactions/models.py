from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from datetime import datetime

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.name

class Transaction(models.Model):
    
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPES,
        default='expense'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"${self.amount:.2f} {self.get_type_display()} - {self.created_at.date()}"
    
    class Meta:
        indexes = [
                models.Index(fields=['user', 'name', 'type', 'category', 'created_at']),
        ]
        ordering = ['-created_at']