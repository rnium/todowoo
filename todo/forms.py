from django.contrib.auth import models
from django.db.models import fields
from django.forms import ModelForm
from .models import Todo

class Todoform(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'important']