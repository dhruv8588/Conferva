from datetime import date
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import modelformset_factory
from django.db.models import Q

from .validators import allow_only_pdf_or_docx_validator

from .models import Author, Conference, Paper


class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ['name', 'acronym', 'research_area', 'venue', 'city', 'country', 'web_page', 'start_date', 'end_date', 'submission_deadline']
        widgets = {
            "start_date": AdminDateWidget(),
            "end_date": AdminDateWidget(),
            "submission_deadline": AdminDateWidget()
        }

    def clean(self):
        cleaned_data = super(ConferenceForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        submission_deadline = cleaned_data.get('submission_deadline')
        # today = date.today()

        # if start_date > end_date:
        #     raise forms.ValidationError("Start date should be earlier than or equal to the end date.")

        # if submission_deadline >= start_date:
        #     raise forms.ValidationError("Submission deadline should be earlier than the start date.")

        # if start_date <= today:
        #     raise forms.ValidationError("Invalid start date. It should be a future date.")

        # if end_date <= today:
        #     raise forms.ValidationError("Invalid end date. It should be a future date.")

        # if submission_deadline < today:
        #     raise forms.ValidationError("Invalid submission deadline. It should be today's date or later.")


class PaperForm(forms.ModelForm):
    # file = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_pdf_or_docx_validator])
    is_submitter_author = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    class Meta:
        model = Paper
        fields = ['title', 'abstract', 'file', 'is_submitter_author'] 
        # fields = ['title', 'abstract', 'authors', 'file']  
  

ConferenceModelFormset = modelformset_factory(
    Conference,
    fields = ['name', 'acronym', 'research_area', 'venue', 'city', 'country', 'web_page', 'start_date', 'end_date', 'submission_deadline', 'is_approved'],
    extra=0,
    widgets={
        'name': forms.HiddenInput(),
    },
)

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'email']
