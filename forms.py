from django import forms
from .models import Staff, Administrator, Tutor

class StaffLoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Staff
        fields = ['staff_name', 'staff_email', 'staff_phone']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError(
                "Password and confirm password do not match"
            )
        return cleaned_data

class AdminLoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Administrator
        fields = ['admin_name', 'admin_email', 'admin_phone']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError(
                "Password and confirm password do not match"
            )
        return cleaned_data


class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['tutor_name', 'education_level', 'subject_taught', 'certificate']

    def __init__(self, *args, **kwargs):
        super(TutorProfileForm, self).__init__(*args, **kwargs)
        self.fields['tutor_name'].widget.attrs['readonly'] = True  # Keep name uneditable