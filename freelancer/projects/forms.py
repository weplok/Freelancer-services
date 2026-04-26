from django.forms import Form, FileField
from django import forms
from django.forms.models import ModelForm

from .models import ProjectModel, FileModel


class ProjectForm(Form):
    name = forms.CharField(max_length=254)
    description = forms.CharField(widget=forms.Textarea)
    customer = forms.CharField(max_length=100)

    class Meta:
        model = ProjectModel
        fields = ("name", "description", "customer")


class ProjectEditForm(ModelForm):
    name = forms.CharField(max_length=254)
    description = forms.CharField(widget=forms.Textarea)
    status = forms.CharField(max_length=20)
    customer = forms.CharField(max_length=100)

    class Meta:
        model = ProjectModel
        fields = ("name", "description", "status", "customer")


class FileForm(Form):
    file = FileField()

    class Meta:
        model = FileModel
        fields = ("file",)


class FileInfoForm(ModelForm):
    readable_filename = forms.CharField(max_length=254)
    version_comment = forms.CharField(max_length=254)

    class Meta:
        model = FileModel
        fields = ("readable_filename", "version_comment")