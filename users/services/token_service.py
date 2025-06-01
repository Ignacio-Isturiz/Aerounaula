import secrets

class TokenService:
    @staticmethod
    def generar():
        return secrets.token_urlsafe(32)
