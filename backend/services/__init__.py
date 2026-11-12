"""Service layer — CineVault's internal API."""
from .auth_service import AuthService, AuthError
from .catalog_service import CatalogService
from .history_service import HistoryService
from .playback_service import PlaybackService

__all__ = [
    "AuthService",
    "AuthError",
    "CatalogService",
    "HistoryService",
    "PlaybackService",
]
