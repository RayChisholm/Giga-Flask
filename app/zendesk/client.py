from zenpy import Zenpy
from zenpy.lib.exception import ZenpyException
from typing import Optional
from flask import current_app
from app.models import ZendeskSettings


class ZendeskClientManager:
    """
    Singleton manager for Zendesk API client.

    This class manages Zenpy client instances and handles credential management.
    It ensures only one client is created and reused across the application.
    """

    _client: Optional[Zenpy] = None
    _credentials_hash: Optional[str] = None

    @classmethod
    def get_client(cls) -> Optional[Zenpy]:
        """
        Get or create a Zenpy client instance.

        Returns:
            Zenpy client instance or None if credentials not configured

        Raises:
            ZenpyException: If connection fails
        """
        # Get credentials from database
        settings = ZendeskSettings.get_active_settings()

        if not settings:
            # Try to get from environment variables as fallback
            subdomain = current_app.config.get('ZENDESK_SUBDOMAIN')
            email = current_app.config.get('ZENDESK_EMAIL')
            token = current_app.config.get('ZENDESK_TOKEN')

            if not all([subdomain, email, token]):
                return None

            credentials = {
                'subdomain': subdomain,
                'email': email,
                'token': token
            }
        else:
            credentials = {
                'subdomain': settings.subdomain,
                'email': settings.email,
                'token': settings.api_token
            }

        # Generate a hash of credentials to detect changes
        current_hash = f"{credentials['subdomain']}{credentials['email']}{credentials['token']}"

        # Create new client if credentials changed or client doesn't exist
        if cls._client is None or cls._credentials_hash != current_hash:
            try:
                creds = {
                    'email': f"{credentials['email']}/token",
                    'token': credentials['token'],
                    'subdomain': credentials['subdomain']
                }

                cls._client = Zenpy(**creds)
                cls._credentials_hash = current_hash
                print(f"Zendesk client created for subdomain: {credentials['subdomain']}")

            except ZenpyException as e:
                print(f"Failed to create Zendesk client: {str(e)}")
                raise

        return cls._client

    @classmethod
    def test_connection(cls) -> tuple[bool, str]:
        """
        Test the Zendesk connection.

        Returns:
            Tuple of (success, message)
        """
        try:
            client = cls.get_client()
            if not client:
                return False, "Zendesk credentials not configured"

            # Try to fetch current user as a simple test
            current_user = client.users.me()
            return True, f"Connection successful! Connected as: {current_user.email}"

        except ZenpyException as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @classmethod
    def clear_client(cls):
        """
        Clear the cached client.
        Useful when credentials are updated.
        """
        cls._client = None
        cls._credentials_hash = None
        print("Zendesk client cache cleared")

    @classmethod
    def is_configured(cls) -> bool:
        """
        Check if Zendesk credentials are configured.

        Returns:
            True if credentials are available
        """
        settings = ZendeskSettings.get_active_settings()
        if settings:
            return True

        # Check environment variables as fallback
        subdomain = current_app.config.get('ZENDESK_SUBDOMAIN')
        email = current_app.config.get('ZENDESK_EMAIL')
        token = current_app.config.get('ZENDESK_TOKEN')

        return all([subdomain, email, token])
