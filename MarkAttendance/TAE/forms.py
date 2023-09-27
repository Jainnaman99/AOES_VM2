from django import forms
from .models import TAESheet

class TAEUploadForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text="max 25 MB"
    )

class TAEUploadMultiForm(forms.Form):
    docfile = forms.FileField(widget=forms.ClearableFileInput(attrs={'directory' : True, 'webkitdirectory' : True}))
