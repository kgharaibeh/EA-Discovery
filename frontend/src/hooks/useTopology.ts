import { useMemo } from 'react';
import type { TopologyResponse } from '../api/types';

interface CytoscapeNodeData {
  id: string;
  label: string;
  assetType: string;
  status: string;
  ipAddresses: string[];
  osFamily?: string;
}

interface CytoscapeEdgeData {
  id: string;
  source: string;
  target: string;
  label: string;
  relationshipType: string;
  confidence: number;
}

interface CytoscapeElement {
  data: CytoscapeNodeData | CytoscapeEdgeData;
  classes?: string;
}

const assetTypeClassMap: Record<string, string> = {
  server: 'node-server',
  database: 'node-database',
  app_server: 'node-app-server',
  application: 'node-application',
  api_endpoint: 'node-api-endpoint',
  network_device: 'node-network-device',
  load_balancer: 'node-load-balancer',
  storage: 'node-storage',
  container: 'node-container',
  virtual_machine: 'node-virtual-machine',
};

function formatRelationshipLabel(type: string): string {
  return type.replace(/_/g, ' ');
}

export function useTopology(topology: TopologyResponse | undefined) {
  const elements = useMemo<CytoscapeElement[]>(() => {
    if (!topology) return [];

    const nodes: CytoscapeElement[] = topology.nodes.map((node) => ({
      data: {
        id: node.id,
        label: node.hostname,
        assetType: node.asset_type,
        status: node.status,
        ipAddresses: node.ip_addresses,
        osFamily: node.os_family,
      },
      classes: `${assetTypeClassMap[node.asset_type] || 'node-unknown'} status-${node.status}`,
    }));

    const edges: CytoscapeElement[] = topology.edges.map((edge) => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: formatRelationshipLabel(edge.relationship_type),
        relationshipType: edge.relationship_type,
        confidence: edge.confidence,
      },
      classes: `edge-${edge.relationship_type}`,
    }));

    return [...nodes, ...edges];
  }, [topology]);

  return { elements };
}
