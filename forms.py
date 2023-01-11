
class LegsManyForm(forms.ModelForm):
    account = TreeNodeChoiceField(
        Account.objects.all(), to_field_name="uuid", required=False
    )
    description = forms.CharField(required=False)
    amount = MoneyField(
        max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, required=False
    )

    class Meta:
        model = Leg
        fields = ("account", "amount", "description")

class TransactionForm(forms.ModelForm):
    description = forms.CharField(label="Transaction notes", required=False)

    class Meta:
        model = Transaction
        fields = [
            "date",
            "description",
        ]
        widgets = {
            "date": DateInput(attrs={"type": "date"}),
            # "description": forms.TextInput(attrs={"class": "form-control"}),
            "description": Textarea(),
        }

    def save(self, commit=True):
        return super(TransactionForm, self).save(commit)

class LegForm(forms.ModelForm):
    account = TreeNodeChoiceField(Account.objects.all(), to_field_name="uuid")
    description = forms.CharField(required=False)
    amount = MoneyField(
        required=True, max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES
    )

    class Meta:
        model = Leg
        fields = ("amount", "account", "description")

    def __init__(self, *args, **kwargs):
        self.statement_line = kwargs.pop("statement_line", None)
        super(LegForm, self).__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount.amount <= 0:
            raise ValidationError("Amount must be greater than zero")

        if self.statement_line and self.statement_line.amount < 0:
            amount *= -1

        return amount
