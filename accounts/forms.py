from django import forms
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField( 
        label="Senha", 
        max_length=15, 
        widget=forms.PasswordInput()
    )

    confirm_password = forms.CharField(
        label="Confirme a Senha", 
        widget=forms.PasswordInput()
    )

    class Meta:
        model = CustomUser
        fields = ('position', 'username', 'registration', 'name', 'admission_date', 'email', 'phone_number', 'password', 'confirm_password',)
        

        widgets = {'admission_date': forms.DateInput (attrs= {'type':'date',}),
                    'position': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("As senhas não coincidem!")
        return cleaned_data