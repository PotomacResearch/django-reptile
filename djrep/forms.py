from django import forms
from django.forms.models import ModelForm
from djrep.models import ReptileTraining
from djrep.tasks import run_training_task
from djrep.types import ReptileTypes
from math import pi



class ReptileTrainingForm(ModelForm):
    num_series = forms.IntegerField(label='Num Series')
    length_series = forms.IntegerField(label='Length Series')
    amplitude_low = forms.FloatField(label='Amplitude Low')
    amplitude_high = forms.FloatField(label='Amplitude High')
    frequency_low = forms.FloatField(label='Frequency Low')
    frequency_high = forms.FloatField(label='Frequency High')
    phase_low = forms.FloatField(label='Phase Low')
    phase_high = forms.FloatField(label='Phase High')

    class Meta:
        model = ReptileTraining
        fields = ["name", "type", "data_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].initial = ReptileTypes.SINE_EXAMPLE
        self.fields['num_series'].initial = 100
        self.fields['length_series'].initial = 1100
        self.fields['amplitude_low'].initial = 0.1
        self.fields['amplitude_high'].initial = 5.0
        self.fields['frequency_low'].initial = 1.0
        self.fields['frequency_high'].initial = 1.0
        self.fields['phase_low'].initial = 0
        self.fields['phase_high'].initial = pi

    def clean_params(self):
        params = self.cleaned_data['params']
        if params is None:
            params = {}
        return params

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.params = {
            'esn': {},
            'autoencoder': {},
            }
        instance.params['library'] = {f: self.cleaned_data[f] for f in
           ['num_series', 'length_series', 'amplitude_low', 'amplitude_high',
            'frequency_low', 'frequency_high', 'phase_low', 'phase_high',
        ]}

        if commit:
            instance.save()
            run_training_task(instance.id)

        return instance
