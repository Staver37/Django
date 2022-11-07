from django import forms

class ConactForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    content = forms.CharField( widget=forms.Textarea)


    