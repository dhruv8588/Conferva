from django import forms
from .models import Editor


class EditorForm(forms.ModelForm):
    class Meta:
        model = Editor
        fields = []
