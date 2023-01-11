class Leg(models.Model):
    uuid = SmallUUIDField(
        default=uuid_default(), editable=False, verbose_name=_("uuid")
    )
    transaction = models.ForeignKey(
        Transaction,
        related_name="legs",
        on_delete=models.CASCADE,
        verbose_name=_("transaction"),
    )
    account = models.ForeignKey(
        Account,
        related_name="legs",
        on_delete=models.CASCADE,
        verbose_name=_("account"),
    )
    amount = MoneyField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        help_text="Record debits as positive, credits as negative",
        default_currency=defaults.INTERNAL_CURRENCY,
        verbose_name=_("amount"),
    )
    description = models.TextField(
        default="", blank=True, verbose_name=_("description")
    )


class Transaction(models.Model):
    uuid = SmallUUIDField(
        default=uuid_default(), editable=False, verbose_name=_("uuid")
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="The creation date of this transaction object",
        verbose_name=_("timestamp"),
    )
    date = models.DateField(
        default=timezone.now,
        help_text="The date on which this transaction occurred",
        verbose_name=_("date"),
    )
    description = models.TextField(
        default="", blank=True, verbose_name=_("description")
    )


class Account(MPTTModel):
    TYPES = Choices(
        ("AS", "asset", "Asset"),  # Eg. Cash in bank
        (
            "LI",
            "liability",
            "Liability",
        ),  # Eg. Loans, bills paid after the fact (in arrears)
        ("IN", "income", "Income"),  # Eg. Sales, housemate contributions
        ("EX", "expense", "Expense"),  # Eg. Office supplies, paying bills
        ("EQ", "equity", "Equity"),  # Eg. Money from shares
        # ("TR", "trading", "Currency Trading"),  # Used to represent currency conversions
    )
    uuid = SmallUUIDField(
        default=uuid_default(), editable=False, verbose_name=_("uuid")
    )
    name = models.CharField(max_length=50, verbose_name=_("name"))
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
        verbose_name=_("parent"),
    )
    code = models.CharField(max_length=3, verbose_name=_("code"))
    full_code = models.CharField(
        max_length=100,
        db_index=True,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("full_code"),
    )
    # TODO: Implement this child_code_width field, as it is probably a good idea
    # child_code_width = models.PositiveSmallIntegerField(default=1)
    type = models.CharField(
        max_length=2, choices=TYPES, blank=True, verbose_name=_("type")
    )
    is_bank_account = models.BooleanField(
        default=False,
        blank=True,
        help_text="Is this a bank account. This implies we can import bank "
        "statements into it and that it only supports a single currency",
        verbose_name=_("is bank account"),
    )
    currencies = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="XAF")
