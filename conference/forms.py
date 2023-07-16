from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import modelformset_factory

from accounts.models import User
from conference.models import Conference, Editor
from paper.models import Reviewer

from .validators import allow_only_pdf_or_docx_validator


class ConferenceForm(forms.ModelForm):
    is_creator_editor = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    class Meta:
        model = Conference
        fields = ['name', 'acronym', 'research_area', 'venue', 'city', 'country', 'web_page', 'start_date', 'end_date', 'submission_deadline', 'is_creator_editor']
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

ConferenceModelFormset = modelformset_factory(
    Conference,
    fields = ['is_approved'],
    extra=0,
    # widgets={
    #     'name': forms.HiddenInput(),
    # },
)

# class ReviewerForm(forms.Form):
#     email = forms.EmailField()       

class EditorForm(forms.ModelForm):
    class Meta:
        model = Editor
        fields = ['first_name', 'last_name', 'email']

class ReviewerForm(forms.ModelForm):
    class Meta:
        model = Reviewer
        fields = ['first_name', 'last_name', 'email']

class InviteUserForm(forms.ModelForm):
    is_invited = forms.BooleanField(required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
      
UserModelFormset = modelformset_factory(
    User,
    # fields = ['first_name', 'last_name'],
    form = InviteUserForm,
    extra = 0,
)        

