import csv
import io

from django import forms
from django.forms.models import ModelForm
from django.db.models.functions.text import Lower

from djrep.models import Reptile, Dataset
from djrep.tasks import run_training_task


class DatasetCreateForm(ModelForm):
    data_file = forms.FileField()

    class Meta:
        model = Dataset
        fields = ["name", "members", "inputs", "outputs"]


    def clean_data_file(self):
        """
        Check that the data file passes basic sanity checks
        """
        csv_file = self.cleaned_data.get('data_file')

        try:
            file_obj = io.StringIO(csv_file.read().decode('UTF-8'))
            Dataset.check_data_file(file_obj,
                                    self.cleaned_data.get('members'),
                                    self.cleaned_data.get('inputs'),
                                    self.cleaned_data.get('outputs'))
        except Exception as e:
            raise forms.ValidationError(f'Error processing CSV file: {e}')

        csv_file.seek(0)
        return csv_file

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.original_filename = self.cleaned_data.get('data_file').name
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
        fields = ["name", "dataset"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['dataset'].queryset = Dataset.objects.filter(
                user__account=user.account).annotate(lower_name=Lower('name')
                                                     ).order_by('lower_name')

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

        if commit:
            instance.save()
            run_training_task(instance.id)

        return instance
