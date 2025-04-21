from django import forms

# ---------------------- LOGIN ----------------------
class LoginForm(forms.Form):
    correo = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Correo electrónico',
            'autocomplete': 'email'
        })
    )
    clave = forms.CharField(
        label="Contraseña",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password'
        })
    )

# ---------------------- REGISTRO ----------------------
class RegistroForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        label="Nombre completo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'})
    )
    correo = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    clave = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    confirmar_clave = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        clave = cleaned_data.get("clave")
        confirmar = cleaned_data.get("confirmar_clave")

        if clave and confirmar and clave != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")


# ---------------------- RECUPERAR CONTRASEÑA ----------------------
class RecuperarClaveForm(forms.Form):
    correo = forms.EmailField(
        label="Correo registrado",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )


# ---------------------- RESTABLECER CONTRASEÑA ----------------------
class RestablecerClaveForm(forms.Form):
    nueva_clave = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    confirmar_clave = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get("nueva_clave")
        confirmar = cleaned_data.get("confirmar_clave")

        if nueva and confirmar and nueva != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")

