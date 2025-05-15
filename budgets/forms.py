from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['amount', 'category', 'month', 'year']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter budget amount',
                'required': True,
                'step': '0.01',
                'min': '0',
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
            'category': forms.Select(attrs={
                'required': True,
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
            'month': forms.NumberInput(attrs={
                'placeholder': 'Enter month (1-12)',
                'required': True,
                'min': '1',
                'max': '12',
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
            'year': forms.NumberInput(attrs={
                'placeholder': 'Enter year',
                'required': True,
                'min': '2000',
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
        }

