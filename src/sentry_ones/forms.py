# coding: utf-8
# -*- coding: utf-8 -*-
from django import forms

class ONESOptionsForm(forms.Form):
  email = forms.CharField(
    max_length=255,
    help_text='ones login email',
    required= True
  )
  password = forms.CharField(
    max_length=255,
    help_text='ones login password',
    required= True
  )
  assign = forms.CharField(
    max_length=255,
    help_text='ones assign id',
    required= True
  )
  project_uuid = forms.CharField(
    max_length=255,
    help_text='ones project_uuidid',
    required= True
  )
  issue_type_uuid = forms.CharField(
    max_length=255,
    help_text='ones issue_type id',
    required=False
  )
  show_log = forms.CharField(
    max_length=255,
    help_text='show log show nshow',
    required=False
  )