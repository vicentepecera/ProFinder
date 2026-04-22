import resend
from django.conf import settings


def _client():
    resend.api_key = settings.RESEND_API_KEY
    return resend.Emails


def enviar_bienvenida(user):
    _client().send({
        "from":    settings.RESEND_FROM,
        "to":      [user.email],
        "subject": "Bienvenido a ProFinder",
        "html": f"""
        <div style="font-family:sans-serif; max-width:520px; margin:auto; padding:2rem;">
          <h2 style="color:#1a56a0;">¡Hola, {user.apodo or user.username}!</h2>
          <p>Tu cuenta en <strong>ProFinder</strong> fue creada exitosamente.</p>
          <p>Ya puedes buscar profesores, agendar clases y gestionar tu perfil.</p>
          <a href="{settings.SITE_URL}/tablero/"
             style="display:inline-block; margin-top:1rem; padding:0.7rem 1.5rem;
                    background:#1a56a0; color:#fff; border-radius:10px;
                    text-decoration:none; font-weight:700;">
            Ir al tablero
          </a>
          <p style="margin-top:2rem; font-size:0.8rem; color:#aaa;">ProFinder · preuniversitario online</p>
        </div>
        """,
    })


def enviar_recuperacion(user, token, uid):
    link = f"{settings.SITE_URL}/recuperar-contrasena/{uid}/{token}/"
    _client().send({
        "from":    settings.RESEND_FROM,
        "to":      [user.email],
        "subject": "Recupera tu contraseña — ProFinder",
        "html": f"""
        <div style="font-family:sans-serif; max-width:520px; margin:auto; padding:2rem;">
          <h2 style="color:#1a56a0;">Recupera tu contraseña</h2>
          <p>Hola, <strong>{user.apodo or user.username}</strong>.</p>
          <p>Recibimos una solicitud para restablecer tu contraseña.
             El enlace expira en <strong>1 hora</strong>.</p>
          <a href="{link}"
             style="display:inline-block; margin-top:1rem; padding:0.7rem 1.5rem;
                    background:#1a56a0; color:#fff; border-radius:10px;
                    text-decoration:none; font-weight:700;">
            Restablecer contraseña
          </a>
          <p style="margin-top:1rem; font-size:0.8rem; color:#aaa;">
            Si no solicitaste esto, ignora este correo.
          </p>
          <p style="font-size:0.8rem; color:#aaa;">ProFinder · preuniversitario online</p>
        </div>
        """,
    })
