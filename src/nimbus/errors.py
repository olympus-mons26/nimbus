"""Application errors with user-facing messages."""


class NimbusError(Exception):
    """Expected application error safe to show to the user."""


class CityNotFoundError(NimbusError):
    """The geocoding service returned no matching city."""


class ConfigurationError(NimbusError):
    """The configuration file could not be read or validated."""


class NetworkError(NimbusError):
    """An API request failed or returned an error."""


class UsageError(NimbusError):
    """The command line contains invalid arguments."""
