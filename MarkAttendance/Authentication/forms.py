from django import forms

months = [1,2,3,4,5,6,7,8,9,10,11,12]
class PasswordResetForm(forms.Form):
    email = forms.EmailField()
    month = forms.ChoiceField(choices=months)