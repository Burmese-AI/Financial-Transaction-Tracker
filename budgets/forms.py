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
                'placeholder': 'Enter year (min: 2000)',
                'required': True,
                'min': '2000',
                'max': '2100',
                'class': 'block w-full border-b border-gray-300 py-3 px-2 text-sm bg-transparent hover:border-gray-400 active:border-gray-500 focus:border-blue-500 focus:outline-none focus:ring-0'
            }),
        }

    def clean_year(self):
        try:
            year = int(self.cleaned_data['year'])
            if year < 2000:
                raise forms.ValidationError("Year must be at least 2000")
            if year > 2100:
                raise forms.ValidationError("Year cannot be greater than 2100")
            return year
        except (ValueError, TypeError):
            raise forms.ValidationError("Please enter a valid year")
        