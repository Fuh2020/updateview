from django.views.generic import DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView

class TransactionsListView(LoginRequiredMixin, ListView):
    
    model = Transaction
    template_name = "transactions/transactions_list.html"
    context_object_name = "transactions"
    ordering = ["-date", "-pk"]
    
from django.forms import inlineformset_factory, formset_factory


class TransactionInline:
    form_class = TransactionForm
    model = Transaction
    template_name = "transactions/transaction_create_or_update.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, "formset_{0}_valid".format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect("hordak:transactions_list")

    def formset_legs_valid(self, formset):
        """
        Hook for custom formset saving.. useful if you have multiple formsets
        """
        legs = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this, if you have can_delete=True parameter set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for leg in legs:
            leg.transaction = self.object
            leg.save()

LegFormSet = inlineformset_factory(
    parent_model=Transaction,
    model=Leg,
    form=LegsManyForm,
    fk_name="transaction",
    extra=4,
    can_delete=False,
)


class TransactionCreate(LoginRequiredMixin, TransactionInline, CreateView):
    def get_context_data(self, **kwargs):
        ctx = super(TransactionCreate, self).get_context_data(**kwargs)
        ctx["named_formsets"] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                 "legs": LegFormSet(prefix="legs"),
             }
        else:
            return {
                 "legs": LegFormSet(
                    self.request.POST or None,
                    self.request.FILES or None,
                    prefix="legs",
                )
             }


class TransactionUpdate(LoginRequiredMixin, TransactionInline, UpdateView):
    def get_context_data(self, **kwargs):
        ctx = super(TransactionUpdate, self).get_context_data(**kwargs)
        ctx["named_formsets"] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            "legs": LegFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="legs",
            )
        }
