import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Category  # Replace with actual app name if needed

User = get_user_model()

CATEGORY_NAMES = [
    "Insurance",
    "Investments",
    "Other",
    "Food",
    "Salary",
    "Rent",
    "Business"
]

CATEGORY_TYPE_MAP = {
    "Insurance": "expense",
    "Investments": "income",
    "Food": "expense",
    "Salary": "income",
    "Rent": "expense",
    "Business": "income",
    "Other": None  # Random
}


class Command(BaseCommand):
    help = 'Seeds ~100 transactions for a selected user.'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        if not users:
            self.stdout.write(self.style.ERROR("No users found."))
            return

        self.stdout.write("Available users:")
        for i, user in enumerate(users, 1):
            self.stdout.write(f"{i}. {user.username}")

        user_index = input("Enter the number of the user to use: ")
        try:
            user = users[int(user_index) - 1]
        except (IndexError, ValueError):
            self.stdout.write(self.style.ERROR("Invalid user selection."))
            return

        self.stdout.write(self.style.SUCCESS(f"Seeding ~100 transactions for {user.username}..."))

        total_transactions = 0
        target_total = 100

        # Shuffle categories and randomly assign transaction counts
        categories = CATEGORY_NAMES[:]
        random.shuffle(categories)

        # Pre-assign a roughly even number of transactions per category
        transactions_per_category = {
            cat: random.randint(10, 20) for cat in categories
        }

        # Adjust total if it goes far off from 100
        factor = target_total / sum(transactions_per_category.values())
        transactions_per_category = {
            cat: max(1, int(count * factor)) for cat, count in transactions_per_category.items()
        }

        for category_name in categories:
            category_obj, _ = Category.objects.get_or_create(name=category_name)
            type_rule = CATEGORY_TYPE_MAP[category_name]
            count = transactions_per_category[category_name]

            for _ in range(count):
                type_ = type_rule if type_rule else random.choice(["income", "expense"])

                transaction = Transaction.objects.create(
                    name=f"{category_name} #{random.randint(1, 9999)}",
                    description=f"A sample {type_} transaction for {category_name}.",
                    amount=round(random.uniform(10.0, 5000.0), 2),
                    user=user,
                    category=category_obj,
                    type=type_
                )
                total_transactions += 1

        self.stdout.write(self.style.SUCCESS(f"Done. {total_transactions} transactions created."))
