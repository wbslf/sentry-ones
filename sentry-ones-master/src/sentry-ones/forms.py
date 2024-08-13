from django import forms

class ONESOptionsForm(forms.Form):
  email = forms.CharField(
    max_length=255,
    help_text='ones login email',
    required= 'true'
  )
  password = forms.CharField(
    max_length=255,
    help_text='ones login password',
    required= 'true'
  )
  assign = forms.CharField(
    max_length=255,
    help_text='ones 负责人用户id',
    required= 'true'
  )
  project_uuid = forms.CharField(
    max_length=255,
    help_text='ones 项目id',
    required= 'true'
  )
  issue_type_uuid = forms.CharField(
    max_length=255,
    help_text='ones 工作项类型id'
  )