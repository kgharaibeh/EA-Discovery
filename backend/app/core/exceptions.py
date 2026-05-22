class EADiscoveryError(Exception):
    pass


class ScanError(EADiscoveryError):
    pass


class ConnectorError(EADiscoveryError):
    pass


class CollectorError(EADiscoveryError):
    pass


class CredentialError(EADiscoveryError):
    pass


class PluginNotFoundError(EADiscoveryError):
    pass


class AssetNotFoundError(EADiscoveryError):
    pass


class RelationshipNotFoundError(EADiscoveryError):
    pass
