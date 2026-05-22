import logging
import re
from typing import Optional
from xml.etree import ElementTree

logger = logging.getLogger(__name__)


class IISConfigParser:
    """Parses IIS applicationHost.config to extract sites, bindings, and app pools."""

    def parse_application_host_config(self, content: str) -> dict:
        """Parse an IIS applicationHost.config file.

        Extracts site definitions, binding information, application pool
        configurations, and virtual directory mappings.

        Args:
            content: Raw XML content of applicationHost.config.

        Returns:
            Dict with 'sites', 'app_pools', and 'bindings' lists.
        """
        sites: list[dict] = []
        app_pools: list[dict] = []
        all_bindings: list[dict] = []

        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as exc:
            logger.debug("Failed to parse applicationHost.config: %s", exc)
            return {"sites": sites, "app_pools": app_pools, "bindings": all_bindings}

        # Parse application pools
        app_pools_section = root.find(".//applicationPools")
        if app_pools_section is not None:
            for pool in app_pools_section.iter("add"):
                pool_info = self._parse_app_pool(pool)
                if pool_info:
                    app_pools.append(pool_info)

        # Parse sites
        sites_section = root.find(".//sites")
        if sites_section is not None:
            for site in sites_section.iter("site"):
                site_info = self._parse_site(site)
                if site_info:
                    sites.append(site_info)
                    all_bindings.extend(site_info.get("bindings", []))

        return {
            "sites": sites,
            "app_pools": app_pools,
            "bindings": all_bindings,
        }

    def _parse_site(self, site_element: ElementTree.Element) -> Optional[dict]:
        """Parse a single <site> element."""
        name = site_element.get("name", "")
        site_id = site_element.get("id", "")

        if not name:
            return None

        site_info: dict = {
            "name": name,
            "id": site_id,
            "bindings": [],
            "applications": [],
        }

        # Parse bindings
        bindings_el = site_element.find("bindings")
        if bindings_el is not None:
            for binding in bindings_el.iter("binding"):
                binding_info = self._parse_binding(binding, name)
                if binding_info:
                    site_info["bindings"].append(binding_info)

        # Parse applications
        for app in site_element.iter("application"):
            app_info = self._parse_application(app)
            if app_info:
                site_info["applications"].append(app_info)

        return site_info

    def _parse_binding(
        self, binding_element: ElementTree.Element, site_name: str
    ) -> Optional[dict]:
        """Parse a single <binding> element."""
        protocol = binding_element.get("protocol", "")
        binding_info_str = binding_element.get("bindingInformation", "")

        if not binding_info_str:
            return None

        # bindingInformation format: ip:port:hostname
        parts = binding_info_str.split(":")
        ip = parts[0] if len(parts) > 0 else "*"
        port = parts[1] if len(parts) > 1 else ""
        hostname = parts[2] if len(parts) > 2 else ""

        return {
            "site_name": site_name,
            "protocol": protocol,
            "ip": ip or "*",
            "port": int(port) if port.isdigit() else 0,
            "hostname": hostname,
            "binding_string": binding_info_str,
        }

    def _parse_application(
        self, app_element: ElementTree.Element
    ) -> Optional[dict]:
        """Parse a single <application> element."""
        path = app_element.get("path", "")
        app_pool = app_element.get("applicationPool", "")

        app_info: dict = {
            "path": path,
            "app_pool": app_pool,
            "virtual_directories": [],
        }

        # Parse virtual directories
        for vdir in app_element.iter("virtualDirectory"):
            vdir_path = vdir.get("path", "")
            physical_path = vdir.get("physicalPath", "")
            if vdir_path or physical_path:
                app_info["virtual_directories"].append({
                    "path": vdir_path,
                    "physical_path": physical_path,
                })

        return app_info

    def _parse_app_pool(self, pool_element: ElementTree.Element) -> Optional[dict]:
        """Parse a single application pool <add> element."""
        name = pool_element.get("name", "")
        if not name:
            return None

        pool_info: dict = {
            "name": name,
            "managed_runtime": pool_element.get("managedRuntimeVersion", ""),
            "managed_pipeline": pool_element.get("managedPipelineMode", ""),
            "auto_start": pool_element.get("autoStart", "true"),
        }

        # Check for process model settings
        process_model = pool_element.find("processModel")
        if process_model is not None:
            pool_info["identity_type"] = process_model.get("identityType", "")
            pool_info["idle_timeout"] = process_model.get("idleTimeout", "")

        # Check for recycling settings
        recycling = pool_element.find("recycling")
        if recycling is not None:
            periodic = recycling.find("periodicRestart")
            if periodic is not None:
                pool_info["recycle_time"] = periodic.get("time", "")

        return pool_info
