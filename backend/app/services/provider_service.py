from app.schemas import ProviderInfoResponse

class ProviderService:
    def __init__(self):
        pass
        
    def get_provider_info(self) -> ProviderInfoResponse:
        """
        Returns lightweight informational structure about provider availability.
        Explicitly does NOT fabricate real hospital or doctor names.
        """
        return ProviderInfoResponse(
            available=False,
            message="Provider search can be connected to a maps or healthcare provider API in a later integration."
        )

provider_service = ProviderService()
