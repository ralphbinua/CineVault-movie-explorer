"""Service layer — CineVault's internal API."""
from .auth_service import AuthService, AuthError
from .catalog_service import CatalogService
from .history_service import HistoryService

__all__ = ["AuthService", "AuthError", "CatalogService", "HistoryService"]
