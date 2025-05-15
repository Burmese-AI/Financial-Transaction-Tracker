from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['name', 'description', 'amount', 'category', 'type']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter transaction name',
                'required': True,
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter description (optional)',
                'rows': 4,
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0 resize-none'
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter amount',
                'required': True,
                'step': '0.01',
                'min': '0',
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
            'category': forms.Select(attrs={
                'required': True,
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
            'type': forms.Select(attrs={
                'required': True,
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
        }