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

class KeywordsForm(forms.ModelForm):
    class Meta:
        model = Keywords
        fields = ['name']

KeywordsFormSet = forms.inlineformset_factory(
    Paper, Keywords, form=KeywordsForm,
    extra=1,
)        
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['body']
    