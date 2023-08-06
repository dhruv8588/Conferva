from django import forms
from paper.models import Author, Keywords, Paper, Review


class PaperForm(forms.ModelForm):
    # file = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), required=False) #, validators=[allow_only_pdf_or_docx_validator]
    is_submitter_author = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    class Meta:
        model = Paper
        fields = ['title', 'abstract', 'file', 'is_submitter_author'] 


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'email']

AuthorModelFormset = forms.modelformset_factory(
    Author,
    fields = ['first_name', 'last_name', 'email'],
    extra = 1,
)

class KeywordsForm(forms.ModelForm):
    class Meta:
        model = Keywords
        fields = ['name']

KeywordsFormSet = forms.inlineformset_factory(
    Paper, Keywords, form=KeywordsForm,
    extra=1,
)        
        
class ReviewForm(forms.ModelForm):
    CHOICES_1 = [
        ('Full length technical paper', 'Full length technical paper'),
        ('Short technical note', 'Short technical note'),
        ('Tutorial/Survey paper', 'Tutorial/Survey paper')
    ]
    CHOICES_2 = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    CHOICES_3 = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    ]
    CHOICES_4 = [
        ('Light', 'Light'),
        ('Moderate', 'Moderate'),
        ('Heavy', 'Heavy'),
        ('None', 'None')
    ]
    CHOICES_5 = [
        ('Accept', 'Accept'),
        ('Minor Revision', 'Minor Revision'),
        ('Major Revision', 'Major Revision'),
        ('Reject and Resubmit', 'Reject and Resubmit'),
        ('Reject', 'Reject')
    ]
    paper_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_1, required=False)
    has_best_paper_award_potential = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2, required=False)
    is_innovative = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2)
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_3)
    anything_to_be_deleted = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2)
    amt_of_copy_editing = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_4, required=False)
    interest_to_engineers = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2)
    will_review_revised_version = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_2, required=False)
    recommendation = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES_5)

    class Meta:
        model = Review
        fields = ['paper_type', 'has_best_paper_award_potential', 'is_innovative', 'rating', 'anything_to_be_deleted', 'what_should_be_deleted', 'amt_of_copy_editing', 'interest_to_engineers', 'will_review_revised_version', 'recommendation', 'comments_to_editor', 'comments_to_author']
    
# class OptionForm(forms.ModelForm):
#     CHOICES = [
#         ('1', 'Option 1'),
#         ('2', 'Option 2'),
#     ]
#     is_chosen = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
#     class Meta:
#         model = Option
#         fields = ['is_chosen']

# OptionModelFormset = forms.modelformset_factory(
#     Option,
#     form = OptionForm,
#     extra = 0
# )