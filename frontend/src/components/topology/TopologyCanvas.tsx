import { useRef, useCallback } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import type { Core, EventObject } from 'cytoscape';

const NODE_STYLES: Record<string, { color: string; shape: string }> = {
  server: { color: '#dae8fc', shape: 'round-rectangle' },
  database: { color: '#d5e8d4', shape: 'ellipse' },
  app_server: { color: '#e1d5e7', shape: 'round-rectangle' },
  application: { color: '#fff2cc', shape: 'round-rectangle' },
  api_endpoint: { color: '#f8cecc', shape: 'diamond' },
  middleware: { color: '#f5f5f5', shape: 'hexagon' },
  load_balancer: { color: '#dae8fc', shape: 'octagon' },
};

const EDGE_COLORS: Record<string, string> = {
  queries: '#2563eb',
  calls_api: '#16a34a',
  hosts: '#9ca3af',
  connects_to: '#6b7280',
  depends_on: '#ea580c',
  authenticates_via: '#7c3aed',
  load_balances: '#0891b2',
  reads_from: '#2563eb',
  writes_to: '#dc2626',
};

interface TopologyCanvasProps {
  elements: cytoscape.ElementDefinition[];
  layout?: string;
  onNodeClick?: (nodeId: string) => void;
  onEdgeClick?: (edgeId: string) => void;
}

const stylesheet: cytoscape.StylesheetStyle[] = [
  {
    selector: 'node',
    style: {
      label: 'data(label)',
      'text-valign': 'bottom',
      'text-margin-y': 8,
      'font-size': '11px',
      'font-family': 'Inter, system-ui, sans-serif',
      width: 50,
      height: 50,
      'border-width': 2,
      'border-color': '#374151',
    },
  },
  ...Object.entries(NODE_STYLES).map(([type, { color, shape }]) => ({
    selector: `node.${type}`,
    style: {
      'background-color': color,
      shape: shape as any,
    },
  })),
  {
    selector: 'node:selected',
    style: {
      'border-width': 3,
      'border-color': '#3b82f6',
      'overlay-color': '#3b82f6',
      'overlay-opacity': 0.15,
    },
  },
  {
    selector: 'edge',
    style: {
      width: 2,
      'curve-style': 'bezier',
      'target-arrow-shape': 'triangle',
      'target-arrow-color': '#6b7280',
      'line-color': '#6b7280',
      'font-size': '9px',
      label: 'data(label)',
      'text-rotation': 'autorotate',
      'text-margin-y': -10,
    },
  },
  ...Object.entries(EDGE_COLORS).map(([type, color]) => ({
    selector: `edge.${type}`,
    style: {
      'line-color': color,
      'target-arrow-color': color,
    },
  })),
  {
    selector: 'edge.queries, edge.reads_from',
    style: { 'line-style': 'dashed' },
  },
  {
    selector: 'edge:selected',
    style: {
      width: 4,
      'overlay-color': '#3b82f6',
      'overlay-opacity': 0.15,
    },
  },
];

export default function TopologyCanvas({ elements, layout = 'cose', onNodeClick, onEdgeClick }: TopologyCanvasProps) {
  const cyRef = useRef<Core | null>(null);

  const handleCyInit = useCallback(
    (cy: Core) => {
      cyRef.current = cy;
      cy.on('tap', 'node', (e: EventObject) => {
        onNodeClick?.(e.target.id());
      });
      cy.on('tap', 'edge', (e: EventObject) => {
        onEdgeClick?.(e.target.id());
      });
    },
    [onNodeClick, onEdgeClick]
  );

  const layoutConfig = {
    name: layout,
    animate: true,
    animationDuration: 500,
    nodeDimensionsIncludeLabels: true,
    ...(layout === 'cose' ? { idealEdgeLength: 150, nodeRepulsion: 8000, gravity: 0.25 } : {}),
  };

  return (
    <CytoscapeComponent
      elements={elements}
      stylesheet={stylesheet}
      layout={layoutConfig}
      cy={handleCyInit}
      className="w-full h-full"
      style={{ width: '100%', height: '100%' }}
    />
  );
}
