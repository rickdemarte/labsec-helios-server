"""
CAS Authentication
"""

import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect

from helios_auth.utils import format_recipient

# UFSC CAS endpoints
CAS_URL = 'https://sistemas.ufsc.br/'
CAS_LOGIN_URL = CAS_URL + 'login?'
# CAS_LOGIN_URL = CAS_URL + 'clientredirect?client_name=gov.br&'
CAS_LOGOUT_URL = CAS_URL + 'logout'
CAS_SAML_VALIDATE_URL = CAS_URL + 'serviceValidate'

# display tweaks
LOGIN_MESSAGE = "Fazer Login"
STATUS_UPDATES = False


def _get_service_url():
    # FIXME current URL
    from helios_auth import url_names
    from django.urls import reverse

    return settings.SECURE_URL_HOST + reverse(url_names.AUTH_AFTER)


def get_auth_url(request, redirect_url):
    request.session['cas_redirect_url'] = redirect_url
    return CAS_LOGIN_URL + 'service=' + urllib.parse.quote(_get_service_url())


def get_saml_info(ticket):
    """Validate CAS ticket and return user info (UFSC).

    UFSC CAS returns XML with namespaces. Depending on the parser, keys may come
    through as `cas:serviceResponse` or just `serviceResponse`.
    """

    url = (
        CAS_SAML_VALIDATE_URL
        + '?service='
        + urllib.parse.quote(_get_service_url())
        + '&ticket='
        + ticket
    )

    req = urllib.request.Request(url)
    raw_response = urllib.request.urlopen(req).read()

    import xmltodict

    data = xmltodict.parse(raw_response)

    def pick(dct, *names):
        """Pick the first matching key from dct, trying with/without `cas:` prefix."""
        if not isinstance(dct, dict):
            return None
        for name in names:
            if name in dct:
                return dct[name]
            if ':' in name:
                # try without prefix
                bare = name.split(':', 1)[1]
                if bare in dct:
                    return dct[bare]
            else:
                # try with cas: prefix
                pref = f"cas:{name}"
                if pref in dct:
                    return dct[pref]
        return None

    service_response = pick(data, 'cas:serviceResponse', 'serviceResponse')
    if not service_response:
        snippet = raw_response[:400]
        raise ValueError(f"CAS: resposta inesperada (sem serviceResponse). Snippet: {snippet!r}")

    auth_success = pick(service_response, 'cas:authenticationSuccess', 'authenticationSuccess')
    if not auth_success:
        # likely authenticationFailure
        auth_failure = pick(service_response, 'cas:authenticationFailure', 'authenticationFailure')
        if isinstance(auth_failure, dict):
            msg = auth_failure.get('#text') or auth_failure.get('message') or str(auth_failure)
        else:
            msg = str(auth_failure)
        raise ValueError(f"CAS: autenticação falhou: {msg}")

    cas_attrs = pick(auth_success, 'cas:attributes', 'attributes')
    if not isinstance(cas_attrs, dict):
        raise ValueError("CAS: autenticação OK, mas sem bloco attributes")

    def attr(name, default=None):
        return pick(cas_attrs, f"cas:{name}", name) or default

    cpf = str(attr('cpf', '')).zfill(11)
    nome = str(attr('nome', ''))
    email = str(attr('email', ''))

    if not cpf.strip() or not nome.strip():
        raise ValueError(f"CAS: attributes incompletos (cpf/nome). attrs keys={list(cas_attrs.keys())}")

    return {
        'type': 'cas',
        'user_id': cpf,
        'name': nome,
        'info': {'email': email} if email else {},
        'token': None,
    }


def get_user_info_after_auth(request):
    ticket = request.GET.get('ticket', None)

    # if no ticket, this is a logout
    if not ticket:
        return None

    user_info = get_saml_info(ticket)
    print(user_info)
    return user_info


def do_logout(user):
    """Perform logout of CAS by redirecting to the CAS logout URL."""
    return HttpResponseRedirect(CAS_URL + 'logout?service=' + settings.SECURE_URL_HOST)


def update_status(token, message):
    """simple update"""
    pass


def send_message(user_id, name, user_info, subject, body):
    send_mail(
        subject,
        body,
        settings.SERVER_EMAIL,
        [format_recipient(name, user_info['email'])],
        fail_silently=False,
        html_message=body,
    )


def check_constraint(constraint, user_info=None, user=None):
    """for eligibility"""
    pass


#
# Election Creation
#

def can_create_election(user_id, user_info):
    return True
