from typing import Generic, TypeVar, Type

T = TypeVar("T")


class PluginRegistry(Generic[T]):
    def __init__(self):
        self._plugins: dict[str, Type[T]] = {}

    def register(self, name: str, plugin_class: Type[T]) -> None:
        self._plugins[name] = plugin_class

    def get(self, name: str) -> Type[T]:
        if name not in self._plugins:
            available = list(self._plugins.keys())
            raise ValueError(f"Plugin '{name}' not registered. Available: {available}")
        return self._plugins[name]

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())

    def create(self, name: str, **kwargs) -> T:
        cls = self.get(name)
        return cls(**kwargs)


traffic_plugin_registry: PluginRegistry = PluginRegistry()
llm_provider_registry: PluginRegistry = PluginRegistry()
credential_backend_registry: PluginRegistry = PluginRegistry()
