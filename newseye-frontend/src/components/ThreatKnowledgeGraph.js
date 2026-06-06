import React, { useState, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { ShieldAlert, Loader2 } from 'lucide-react';

const ThreatKnowledgeGraph = ({ onNodeClick }) => {
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchGraphData = async () => {
            try {
                // In a real dev environment, this would be the actual API URL
                const response = await fetch('http://127.0.0.1:8000/api/v1/analytics/graph');
                if (!response.ok) throw new Error('Failed to fetch graph data');
                const data = await response.json();
                setGraphData(data);
                setLoading(false);
            } catch (err) {
                console.error('Error loading graph:', err);
                setError(err.message);
                setLoading(false);
            }
        };

        fetchGraphData();
    }, []);

    const getNodeColor = (node) => {
        switch (node.label) {
            case 'News': return '#3b82f6'; // Blue
            case 'CrimeType': return '#ef4444'; // Red
            case 'Organization': return '#f59e0b'; // Amber
            case 'Person': return '#10b981'; // Green
            case 'Location': return '#8b5cf6'; // Purple
            case 'Source': return '#64748b'; // Slate
            default: return '#94a3b8';
        }
    };

    const handleNodeClick = (node) => {
        if (onNodeClick) {
            onNodeClick(node);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-96 bg-white rounded-xl shadow-sm">
                <Loader2 className="animate-spin text-blue-500 mb-4" size={40} />
                <p className="text-gray-500">지식 그래프 데이터를 불러오는 중...</p>
            </div>
        );
    }

    if (error || graphData.nodes.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-96 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
                <ShieldAlert className="text-gray-400 mb-4" size={40} />
                <p className="text-gray-500">표시할 그래프 데이터가 없습니다.</p>
                <p className="text-xs text-gray-400 mt-2">뉴스가 인제스트되면 자동으로 그래프가 형성됩니다.</p>
            </div>
        );
    }

    return (
        <div className="threat-knowledge-graph bg-white p-6 rounded-xl shadow-sm border border-gray-100 my-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-800 flex items-center">
                    <ShieldAlert className="mr-2 text-red-500" size={24} />
                    Threat Intelligence Knowledge Graph
                </h3>
                <div className="flex gap-4 text-xs">
                    <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-blue-500 mr-1"></span>뉴스</div>
                    <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-red-500 mr-1"></span>범죄유형</div>
                    <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-amber-500 mr-1"></span>기관</div>
                    <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-green-500 mr-1"></span>인물</div>
                </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg overflow-hidden border border-gray-200" style={{ height: '500px' }}>
                <ForceGraph2D
                    graphData={graphData}
                    nodeLabel={(node) => `[${node.label}] ${node.name}`}
                    nodeColor={getNodeColor}
                    nodeRelSize={6}
                    onNodeClick={handleNodeClick}
                    linkDirectionalParticles={2}
                    linkDirectionalParticleSpeed={0.005}
                    linkLabel={(link) => link.type}
                    linkWidth={1.5}
                    backgroundColor="#f8fafc"
                    width={800} // This should ideally be responsive
                    height={500}
                />
            </div>
            
            <p className="text-xs text-gray-400 mt-4 text-center">
                * 노드를 클릭하여 관련 뉴스를 탐색하거나 드래그하여 위치를 조정할 수 있습니다.
            </p>
        </div>
    );
};

export default ThreatKnowledgeGraph;
