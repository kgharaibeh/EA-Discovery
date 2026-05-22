import { useQuery } from '@tanstack/react-query';
import { getTopology } from '../api/relationships';
import { useTopology } from '../hooks/useTopology';
import { useTopologyStore } from '../stores/useTopologyStore';
import TopologyCanvas from '../components/topology/TopologyCanvas';
import TopologyControls from '../components/topology/TopologyControls';
import TopologyFilters from '../components/topology/TopologyFilters';
import TopologyLegend from '../components/topology/TopologyLegend';
import NodeDetail from '../components/topology/NodeDetail';
import EdgeDetail from '../components/topology/EdgeDetail';

export default function TopologyPage() {
  const { data: topology, isLoading } = useQuery({
    queryKey: ['topology'],
    queryFn: getTopology,
  });

  const { elements } = useTopology(topology);
  const { selectedNodeId, selectedEdgeId, layout, setSelectedNode, setSelectedEdge } = useTopologyStore();

  const selectedEdge = topology?.edges.find((e) => e.id === selectedEdgeId);

  if (isLoading) {
    return <div className="flex items-center justify-center h-full text-gray-500">Loading topology...</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Topology Map</h1>
        <TopologyControls />
      </div>

      <div className="flex flex-1 gap-4 min-h-0">
        <TopologyFilters />

        <div className="flex-1 bg-white rounded-lg shadow border relative">
          {elements.length > 0 ? (
            <TopologyCanvas
              elements={elements as any}
              layout={layout}
              onNodeClick={setSelectedNode}
              onEdgeClick={setSelectedEdge}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              No topology data. Run a scan to discover assets and relationships.
            </div>
          )}
          <div className="absolute bottom-4 left-4">
            <TopologyLegend />
          </div>
        </div>

        {selectedNodeId && (
          <div className="w-80 shrink-0">
            <NodeDetail assetId={selectedNodeId} onClose={() => setSelectedNode(null)} />
          </div>
        )}
        {selectedEdge && (
          <div className="w-80 shrink-0">
            <EdgeDetail edge={selectedEdge} onClose={() => setSelectedEdge(null)} />
          </div>
        )}
      </div>
    </div>
  );
}
