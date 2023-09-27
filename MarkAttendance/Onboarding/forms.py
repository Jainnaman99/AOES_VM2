from .models import Resource
from django import forms

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = '__all__'
        # widgets = {
        #     'EmpCode': fm.Input(attrs={'onchange':'update_func()'},),
        # }
        


class ResetForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['EmpCode']
        