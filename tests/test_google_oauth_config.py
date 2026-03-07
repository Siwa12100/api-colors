import pytest
from app.routes.authentication import verifier_configuration_google


@pytest.mark.integration
def test_google_oauth_configuration():
    """
    Test réel de la configuration OAuth Google.
    """
    assert verifier_configuration_google() is True
