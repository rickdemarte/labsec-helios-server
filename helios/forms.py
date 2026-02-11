"""
Forms for Helios
"""

from django import forms
from django.conf import settings

from .fields import DateTimeLocalField
from .models import Election


class ElectionForm(forms.Form):
  short_name = forms.SlugField(
    max_length=40,
    label='nome curto',
    help_text='sem espaços; fará parte da URL da sua eleição, por exemplo: meu-clube-2010'
  )
  name = forms.CharField(
    max_length=100,
    label='nome',
    widget=forms.TextInput(attrs={'size': 60}),
    help_text='nome amigável da sua eleição, por exemplo: Eleição do Meu Clube 2010'
  )
  description = forms.CharField(
    max_length=4000,
    label='descrição',
    widget=forms.Textarea(attrs={'cols': 70, 'wrap': 'soft'}),
    required=False
  )
  election_type = forms.ChoiceField(label='tipo', choices=Election.ELECTION_TYPES)
  use_voter_aliases = forms.BooleanField(
    required=False,
    initial=False,
    label='usar apelidos (aliases) para eleitores',
    help_text='se selecionado, as identidades dos eleitores serão substituídas por apelidos, ex.: "V12", no centro de rastreamento de cédulas'
  )
  # use_advanced_audit_features = forms.BooleanField(required=False, initial=True, help_text='disable this only if you want a simple election with reduced security but a simpler user interface')
  randomize_answer_order = forms.BooleanField(
    required=False,
    initial=False,
    label='randomizar ordem das respostas',
    help_text='habilite se você quiser que as alternativas apareçam em ordem aleatória para cada eleitor'
  )
  private_p = forms.BooleanField(
    required=False,
    initial=False,
    label='Privada?',
    help_text='uma eleição privada é visível apenas para eleitores registrados.'
  )
  help_email = forms.CharField(
    required=False,
    initial='',
    label='E-mail de suporte',
    help_text='endereço de e-mail que os eleitores devem contatar se precisarem de ajuda.'
  )

  if settings.ALLOW_ELECTION_INFO_URL:
    election_info_url = forms.CharField(
      required=False,
      initial='',
      label='URL para download de informações da eleição',
      help_text='URL de um documento PDF com informações adicionais da eleição, por exemplo: biografias e propostas de candidatos'
    )

  # times
  voting_starts_at = DateTimeLocalField(
    label='Início da votação',
    help_text='data e hora em UTC em que a votação começa',
    required=False
  )
  voting_ends_at = DateTimeLocalField(
    label='Término da votação',
    help_text='data e hora em UTC em que a votação termina',
    required=False
  )


class ElectionTimeExtensionForm(forms.Form):
  voting_extended_until = DateTimeLocalField(
    label='Votação estendida até',
    help_text='data e hora em UTC até quando a votação foi estendida',
    required=False
  )


class EmailVotersForm(forms.Form):
  subject = forms.CharField(max_length=80, label='Assunto')
  body = forms.CharField(max_length=4000, widget=forms.Textarea, label='Mensagem')
  send_to = forms.ChoiceField(
    label='Enviar para',
    initial='all',
    choices=[
      ('all', 'todos os eleitores'),
      ('voted', 'eleitores que já votaram'),
      ('not-voted', 'eleitores que ainda não votaram'),
    ]
  )


class TallyNotificationEmailForm(forms.Form):
  subject = forms.CharField(max_length=80, label='Assunto')
  body = forms.CharField(max_length=2000, widget=forms.Textarea, label='Mensagem', required=False)
  send_to = forms.ChoiceField(
    label='Enviar para',
    choices=[
      ('all', 'todos os eleitores'),
      ('voted', 'somente eleitores que votaram'),
      ('none', 'ninguém — tem certeza?'),
    ]
  )


class VoterPasswordForm(forms.Form):
  voter_id = forms.CharField(max_length=50, label='ID do eleitor')
  password = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='Senha')


class VoterPasswordResendForm(forms.Form):
  voter_id = forms.CharField(
    max_length=50,
    label='ID do eleitor',
    help_text='Digite o ID de eleitor que você recebeu para esta eleição'
  )
