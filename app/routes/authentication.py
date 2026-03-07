"""
Authentication routes for the Colors API.
"""

import os
import datetime
import requests as http_requests
import jwt
from flask import Blueprint, request, jsonify, redirect
from functools import wraps
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

JWT_SECRET_KEY = os.getenv("SECRET_KEY")

JWT_EXPIRATION_HOURS = 24

GOOGLE_AUTH_URL = os.getenv("GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL")
GOOGLE_USERINFO_URL = os.getenv("GOOGLE_USERINFO_URL")


def generer_token_jwt(utilisateur):
    """
    Creates a signed JWT token containing the user's information.

    The token contains:
      - user_id  : the database identifier
      - email    : the user's email address
      - role     : their role (admin or user)
      - exp      : the token expiration date
      - iat      : the token creation date
    """
    date_expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        hours=JWT_EXPIRATION_HOURS
    )

    payload = {
        "user_id": utilisateur.id,
        "email": utilisateur.email,
        "role": utilisateur.role,
        "exp": date_expiration,
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

    return token


def decoder_token_jwt(token):
    """
    Decodes a JWT token and returns the payload (data).
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # The token has expired
        return None
    except jwt.InvalidTokenError:
        # The token is invalid (bad signature, incorrect format, etc.)
        return None


def jwt_requis(fonction_route):
    """
    Decorator that requires JWT authentication for protected routes.
    """

    @wraps(fonction_route)
    def wrapper(*args, **kwargs):

        header_authorization = request.headers.get("Authorization")

        if header_authorization is None:
            return jsonify({"error": "Missing token. Add the header: Authorization: Bearer <token>"}), 401

        parties = header_authorization.split(" ")

        if len(parties) != 2 or parties[0] != "Bearer":
            return jsonify({"error": "Invalid header format. Use: Bearer <token>"}), 401

        token = parties[1]

        payload = decoder_token_jwt(token)

        if payload is None:
            return jsonify({"error": "Invalid or expired token"}), 401

        utilisateur_courant = db.session.get(User, payload["user_id"])

        if utilisateur_courant is None:
            return jsonify({"error": "User not found"}), 401

        if not utilisateur_courant.is_active:
            return jsonify({"error": "This account has been disabled"}), 403

        return fonction_route(utilisateur_courant=utilisateur_courant, *args, **kwargs)

    return wrapper


@auth_bp.route("/login", methods=["GET"])
def login():
    """
    Builds the Google authorization URL and redirects the user.

    Google will ask the user to sign in with their account,
    then redirect back to /auth/callback with a "code".
    """
    parametres = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",          # We want to receive a "code" in return
        "scope": "openid email profile",  # We request the email and profile
        "access_type": "offline",         # To obtain a refresh token (optional)
        "prompt": "consent",              # Force the consent screen to appear
    }

    # Build the full URL manually for clarity
    liste_parametres = []
    for cle, valeur in parametres.items():
        liste_parametres.append(f"{cle}={valeur}")

    url_complete = GOOGLE_AUTH_URL + "?" + "&".join(liste_parametres)

    # Redirect the user to Google
    return redirect(url_complete)



@auth_bp.route("/callback", methods=["GET"])
def callback():
    """
    This route is called by Google after the user has signed in.
    Google sends a "code" in the URL query string.
    """
    code_google = request.args.get("code")

    if code_google is None:
        return jsonify({"error": "Authorization code missing from Google"}), 400

    # Send a POST request to Google with the code
    donnees_echange = {
        "code": code_google,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    reponse_google_token = http_requests.post(GOOGLE_TOKEN_URL, data=donnees_echange)

    # Check that Google responded successfully
    if reponse_google_token.status_code != 200:
        return jsonify({"error": "Failed to exchange the code with Google"}), 400

    # Extract the access_token from the JSON response
    donnees_token = reponse_google_token.json()
    access_token = donnees_token.get("access_token")

    if access_token is None:
        return jsonify({"error": "Access token missing from Google response"}), 400

    # Call the Google userinfo API with the access_token
    headers_google = {"Authorization": f"Bearer {access_token}"}
    reponse_google_profil = http_requests.get(GOOGLE_USERINFO_URL, headers=headers_google)

    if reponse_google_profil.status_code != 200:
        return jsonify({"error": "Failed to retrieve Google profile"}), 400

    profil_google = reponse_google_profil.json()
    email_google = profil_google.get("email")
    nom_complet_google = profil_google.get("name", "")

    if email_google is None:
        return jsonify({"error": "Email not available in Google profile"}), 400

    utilisateur = User.query.filter_by(email=email_google).first()

    if utilisateur is None:
        # The email is NOT in the whitelist -> access denied
        return jsonify({
            "error": "Access denied",
            "message": f"The email {email_google} is not authorized. "
                       f"Contact an administrator to be added."
        }), 403

    if not utilisateur.is_active:
        return jsonify({
            "error": "Account disabled",
            "message": "Your account has been disabled by an administrator."
        }), 403

    utilisateur.full_name = nom_complet_google
    utilisateur.last_login_at = datetime.datetime.now(datetime.timezone.utc)
    db.session.commit()

    token = generer_token_jwt(utilisateur)

    # Rediriger vers le frontend Angular avec le JWT dans l'URL
    # Angular va lire ce token et le stocker dans localStorage
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")
    return redirect(
        f"{frontend_url}/auth/callback?token={token}"
        f"&email={utilisateur.email}"
        f"&full_name={utilisateur.full_name}"
        f"&role={utilisateur.role}"
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_requis
def me(utilisateur_courant):
    """
    Route protected by the @jwt_requis decorator.
    Simply returns the profile of the currently logged-in user.

    To call this route, send the header:
        Authorization: Bearer <jwt_token>
    """
    return jsonify({
        "id": utilisateur_courant.id,
        "email": utilisateur_courant.email,
        "full_name": utilisateur_courant.full_name,
        "role": utilisateur_courant.role,
        "is_active": utilisateur_courant.is_active,
        "last_login_at": (
            utilisateur_courant.last_login_at.isoformat()
            if utilisateur_courant.last_login_at
            else None
        ),
    }), 200

def verifier_configuration_google():
    """
    Vérifie que la configuration OAuth Google est valide.
    Teste si le endpoint token répond correctement.
    """
    if not GOOGLE_CLIENT_ID:
        raise ValueError("GOOGLE_CLIENT_ID manquant")

    if not GOOGLE_CLIENT_SECRET:
        raise ValueError("GOOGLE_CLIENT_SECRET manquant")

    if not GOOGLE_AUTH_URL:
        raise ValueError("GOOGLE_AUTH_URL manquant")

    if not GOOGLE_TOKEN_URL:
        raise ValueError("GOOGLE_TOKEN_URL manquant")

    # Test simple : requête GET sur l'endpoint auth
    response = http_requests.get(GOOGLE_AUTH_URL)

    if response.status_code != 200:
        raise ConnectionError("Impossible de joindre GOOGLE_AUTH_URL")

    return True
