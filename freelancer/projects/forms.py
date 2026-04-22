from django.forms import Form, FileField
from django import forms

from .models import ProjectModel, FileModel


class ProjectForm(Form):
    name = forms.CharField(max_length=254)
    description = forms.Textarea()
    customer = forms.CharField(max_length=100)

    class Meta:
        model = ProjectModel
        fields = ("name", "description", "customer")


class FileForm(Form):
    file = FileField()

    class Meta:
        model = FileModel
        fields = ("file",)
