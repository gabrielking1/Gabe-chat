from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
# from django import request
from django.db.models import fields
from django.utils.text import slugify
from django_countries.widgets import CountrySelectWidget
# from django_countries.fields import CountryField
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# from Home.filechecker import validate_file_size

class RegForm(UserCreationForm):

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            validate_email(email)
            if email and User.objects.filter(email=email).exists():
                self.add_error('email', 'This email address is already in use.')
        except ValidationError:
            raise forms.ValidationError('Enter a valid email address(e.g. Example@hello.com')
        return email
    class Meta:
        model = User
        fields = ('first_name','last_name', 'username', 'email', 'password1' ,'password2' )
	

# class UploadForm(forms.ModelForm):
#     image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
#     height = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your height in cm', 'class': 'form-control'}))
    
#     class Meta:
#         model = Upload
#         fields = '__all__'
    
#     def __init__(self, *args, **kwargs):
#         super(UploadForm, self).__init__(*args, **kwargs)
#         self.fields['username'].widget = forms.HiddenInput()