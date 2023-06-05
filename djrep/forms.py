from django.forms.models import ModelForm
from djrep.models import ReptileTraining



class ReptileTrainingForm(ModelForm):
    class Meta:
        model = ReptileTraining
        fields = ["name", ]
