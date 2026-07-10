"""Domain-specific errors raised by Coleasing."""


class LeaseError(Exception):
    """Base class for lease failures."""


class LeaseUnavailableError(LeaseError):
    """Raised when another owner currently holds a lease."""


class LeaseLostError(LeaseError):
    """Raised when renewing a lease whose ownership or TTL was lost."""


class LeaseNotOwnedError(LeaseError):
    """Raised when releasing a lease owned by someone else or already expired."""
