from traffic.plugin_registry import PluginRegistry
from intelligence.providers.base import AbstractLLMProvider

llm_registry: PluginRegistry[AbstractLLMProvider] = PluginRegistry()
