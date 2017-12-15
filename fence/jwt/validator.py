import datetime
import flask
import flask_oauthlib
import jwt

from . import keys
from cdispyutils import auth
from .blacklist import BlacklistedToken


class JWTValidator(flask_oauthlib.provider.OAuth2RequestValidator):
    """
    Validator for JWTs used in the OAuth2 procedure. This class provides a
    validator for Flask's OAuth component, redefining bearer and refresh token
    validation of ``flask_oauthlib.oauth2.OAuth2RequestValidator`` to use JWT
    instead.

    .. code-block:: python

        oauth = OAuth2Provider()
        oauth._validator = JWTValidator()

    An example JWT following the specifications for this implementation:

    .. code-block:: python

        {
            "sub": "1234567",
            "iss": "dcfauth:56fc3842ccf2c1c7ec5c5d14",
            "iat": 1459458458,
            "exp": 1459487258,
            "jti": "f8733984-8164-4689-9c25-56707962d7e0",
            "aud": [
                "access",
                "data",
                "iam",
            ],
            "context": {
                "user": {
                    "name": "NIH_USERNAME",
                    "projects": {
                        "phs000178": ["member"],
                        "phs000218": ["member", "submitter"],
                    },
                    "email": "user@university.edu",
                }
            }
        }
    """

    def validate_bearer_token(self, token, scopes, request):
        """
        Define ``flask_oauthlib.oauth2.OAuth2Provider.validate_bearer_token``
        to validate a JWT access token.

        Per `flask_oauthlib`, validate:
        #. if the token is available
        #. if the token has expired
        #. if the scopes are available

        Args:
            token (str): in this implementation, an encoded access JWT
            scopes (List[str]): list of scopes
            request (oauthlib.common.Request): oauth request to serve

        Return:
            bool: whether token is valid
        """

        def fail_with(msg):
            request.error_message = msg
            flask.current_app.logger.exception(msg)
            return False

        # Validate token existing.
        if not token:
            return fail_with('No token provided.')

        aud = set(scopes)
        # The token must contain an `'access'` audience (i.e. be an access, not
        # refresh token).
        aud.update('access')
        try:
            decoded_jwt = auth.validate_request_jwt(aud)
        except auth.JWTValidationError as e:
            return fail_with(str(e))

        flask.current_app.logger.info(
            'validated access token: ' + str(decoded_jwt)
        )

        return True

    def validate_refresh_token(
            self, refresh_token, client, request, *args, **kwargs):
        """
        Validate a JWT refresh token.

        Args:
            refresh_token (str): in this implementation, an encoded refresh JWT
            client (Client): the client
            request (oauthlib.common.Request): OAuth HTTP request to serve

        Return:
            bool: whether token is valid
        """

        def fail_with(msg):
            request.error_message = msg
            flask.current_app.logger.exception(msg)
            return False

        # Validate token existing.
        if not refresh_token:
            return fail_with('No token provided.')

        # Must contain just a `'refresh'` audience for a refresh token.
        decoded_jwt = auth.validate_jwt(
            encoded_token=refresh_token,
            public_key=keys.default_public_key(),
            aud={'refresh'},
            iss=flask.current_app.config['HOST_NAME'],
        )

        # Validate jti and make sure refresh token is not blacklisted.
        jti = decoded_jwt.get('jti')
        if not jti:
            return fail_with('Token missing jti claim.')
        with flask.current_app.db.session as session:
            if session.query(BlacklistedToken).filter_by(jti=jti).first():
                return fail_with('Token is blacklisted.')

        flask.current_app.logger.info(
            'validated refresh token: ' + str(decoded_jwt)
        )

        return True

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        """
        The docs on this method from flask-oauthlib:

            Get the list of scopes associated with the refresh token.

            This method is used in the refresh token grant flow. We return the
            scope of the token to be refreshed so it can be applied to the new
            access token.

        This method is slightly weird in the JWT implementation, firstly since
        the token is just a string (so does not have a ``scopes`` attribute),
        and also because the ``scopes`` are translated into the ``aud`` field
        in the JWT.
        """
        return jwt.decode(refresh_token, verify=False)['access_aud']
