from django.forms.models import ModelForm
from djrep.models import ReptileTraining
from djrep.tasks import run_dummy_task



class ReptileTrainingForm(ModelForm):
    class Meta:
        model = ReptileTraining
        fields = ["name", ]

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
            run_dummy_task(instance.id)

        return instance
