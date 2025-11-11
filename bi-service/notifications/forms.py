from django import forms
from django.contrib.auth.models import User
from ingestion.models import DataSource
from .models import KPI, AlertRule

class KPIForm(forms.ModelForm):
    class Meta:
        model = KPI
        fields = ['name', 'description', 'data_source', 'table_name', 'metric_type', 'column_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Total Ventas Mensuales'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe qué mide este KPI...'}),
            'data_source': forms.Select(attrs={'class': 'form-control'}),
            'table_name': forms.Select(attrs={'class': 'form-control'}),
            'metric_type': forms.Select(attrs={'class': 'form-control'}),
            'column_name': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['data_source'].queryset = DataSource.objects.filter(
                owner=user,
                internal_schema__isnull=False
            ).exclude(internal_schema='')
        
        self.fields['column_name'].widget = forms.Select(attrs={'class': 'form-control'})
        self.fields['column_name'].choices = [('', 'Selecciona primero una fuente de datos')]

class AlertRuleForm(forms.ModelForm):
    email_recipients_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'email1@ejemplo.com, email2@ejemplo.com'
        }),
        help_text='Emails separados por comas (opcional)'
    )
    
    class Meta:
        model = AlertRule
        fields = [
            'name', 'kpi', 'comparison_operator', 'threshold_value', 
            'severity', 'send_email', 'send_in_app'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ventas por debajo del mínimo'}),
            'kpi': forms.Select(attrs={'class': 'form-control'}),
            'comparison_operator': forms.Select(attrs={'class': 'form-control'}),
            'threshold_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'send_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_in_app': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        initial_kpi = kwargs.pop('initial_kpi', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['kpi'].queryset = KPI.objects.filter(owner=user, is_active=True)
        
        if initial_kpi:
            self.fields['kpi'].initial = initial_kpi
            self.fields['kpi'].widget.attrs['readonly'] = True
        
        if not self.instance.pk and user:
            self.initial['email_recipients_text'] = user.email
    
    def clean_email_recipients_text(self):
        """Valida y convierte emails de texto a lista"""
        emails_text = self.cleaned_data.get('email_recipients_text', '')
        if not emails_text:
            return []
        
        emails = [email.strip() for email in emails_text.split(',') if email.strip()]
        
        for email in emails:
            if not forms.EmailField().clean(email):
                raise forms.ValidationError(f'Email inválido: {email}')
        
        return emails
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        emails = self.cleaned_data.get('email_recipients_text', [])
        instance.email_recipients = emails
        
        if commit:
            instance.save()
        return instance