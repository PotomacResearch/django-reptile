import os

from django import forms
from django.forms.models import ModelForm
from djrep.models import Reptile, Dataset
from djrep.tasks import run_training_task
from djrep.reptile import ReptileParams


class DatasetCreateForm(ModelForm):
    data_file = forms.FileField(required=False)

    class Meta:
        model = Dataset
        fields = ["name"]

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
            instance.save_source_csv(self.cleaned_data.get('data_file'))

        return instance


class ReptileCreateForm(ModelForm):
    input_dimension = forms.IntegerField(label='ESN Input Dimension')
    size = forms.IntegerField(label='ESN Size')
    connections = forms.IntegerField(label='ESN Connections')
    spectral_radius = forms.FloatField(label='ESN Spectral Radius')
    input_strength = forms.FloatField(label='ESN Input Strength')
    bias_strength = forms.FloatField(label='ESN Bias Strength')
    leaking_rate = forms.FloatField(label='ESN Leaking Rate')

    input_dim = forms.IntegerField(label='Autoencoder Input Dimension')
    hidden_dim1 = forms.IntegerField(label='Autoencoder Hidden Dimension 1')
    hidden_dim2 = forms.IntegerField(label='Autoencoder Hidden Dimension 2')
    encoder_dim = forms.IntegerField(label='Autoencoder Encoder Dimension')
    learning_rate = forms.FloatField(label='Autoencoder Learning Rate')
    bounded_latent = forms.BooleanField(label='Autoencoder Bounded Latent?')

    class Meta:
        model = Reptile
        fields = ["name", ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ESN
        self.fields['input_dimension'].initial = 2
        self.fields['size'].initial = 250
        self.fields['connections'].initial = 25
        self.fields['spectral_radius'].initial = 1.1
        self.fields['input_strength'].initial = 0.25
        self.fields['bias_strength'].initial = 1.5
        self.fields['leaking_rate'].initial = 0.014

        # Autoencoder
        self.fields['input_dim'].initial = 500
        self.fields['hidden_dim1'].initial = 500
        self.fields['hidden_dim2'].initial = 200
        self.fields['encoder_dim'].initial = 3
        self.fields['learning_rate'].initial =  0.0001
        self.fields['bounded_latent'].initial = True


    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.params = {
            'library': {},
            }
        instance.params['esn'] = {f: self.cleaned_data[f] for f in
            ['input_dimension', 'size', 'connections', 'spectral_radius',
             'input_strength', 'bias_strength', 'leaking_rate',
        ]}
        instance.params['autoencoder'] = {f: self.cleaned_data[f] for f in
            ['input_dim', 'encoder_dim', 'learning_rate', 'bounded_latent',
        ]}
        instance.params['autoencoder']['hidden_dim'] = \
            [self.cleaned_data['hidden_dim1'], self.cleaned_data['hidden_dim2']]

        file_data = self.cleaned_data.get('data_file')

        if commit:
            instance.save()
            if file_data:
                training_dir = Reptile.get_base_save_path(
                                        instance.id) / ReptileParams.data_path
                os.makedirs(training_dir, exist_ok=True)
                with open(training_dir / ReptileParams.datafile_name,
                          'wb') as f:
                    for chunk in file_data.chunks():
                        f.write(chunk)
            run_training_task(instance.id)

        return instance
