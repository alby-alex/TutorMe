from django import forms

class SignUpForm(forms.Form):
	#TODO: change this to a selecty box thing
	roles = [('student', 'Student'), ('tutor', 'Tutor')]
	Signup = forms.ChoiceField(label="Choose your Role", choices= roles, widget=forms.RadioSelect())

class HourlyRateForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.label_suffix = ""
	rate = forms.DecimalField(label = "Hourly Rate: $", max_digits = 5, decimal_places = 2)

class TutorBioForm(forms.Form):
	bio = forms.CharField(widget=forms.Textarea(attrs={"rows":"4"}), label = '')
