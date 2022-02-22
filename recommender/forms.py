from django import forms

class SearchForm(forms.Form):
    artist = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    song_name = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    album = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), required=False)
    from_year = forms.IntegerField(required=False)
    to_year = forms.IntegerField(required=False)
