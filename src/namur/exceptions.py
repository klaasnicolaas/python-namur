"""Asynchronous Python client providing Open Data information of Namur."""


class ODPNamurError(Exception):
    """Generic Open Data Platform Namur exception."""


class ODPNamurConnectionError(ODPNamurError):
    """Open Data Platform Namur - connection exception."""


class ODPNamurResultsError(ODPNamurError):
    """Open Data Platform Namur - no results exception."""
