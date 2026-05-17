import { useEffect } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Panel,
  useNodesState,
  useEdgesState,
} from 'reactflow'
import 'reactflow/dist/style.css'

import SystemNode from './components/SystemNode'
import { useSystemStatus } from './hooks/useSystemStatus'
import { initialNodes, initialEdges } from './data/graph'
import './App.css'

const nodeTypes = { systemNode: SystemNode }

export default function App() {
  const status = useSystemStatus()
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  useEffect(() => {
    setNodes((prev) =>
      prev.map((node) => ({
        ...node,
        data: {
          ...node.data,
          status:
            node.id === 'client'
              ? 'online'
              : status[node.data.statusKey] ?? 'unknown',
        },
      }))
    )
  }, [status, setNodes])

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        fitViewOptions={{ padding: 0.25 }}
      >
        <Background color="#1e293b" gap={24} size={1} />
        <Controls />
        <MiniMap
          nodeColor={() => '#1e293b'}
          maskColor="rgba(2, 6, 23, 0.8)"
          style={{ background: '#0f172a', border: '1px solid #1e293b' }}
        />
        <Panel position="top-left">
          <div className="legend">
            <span className="legend-title">Sistema — Arquitetura Live</span>
            <div className="legend-items">
              <span className="dot online" /> online
              <span className="dot offline" /> offline
              <span className="dot unknown" /> desconhecido
            </div>
          </div>
        </Panel>
        <Panel position="top-right">
          <div className="poll-info">polling a cada 5s</div>
        </Panel>
      </ReactFlow>
    </div>
  )
}
