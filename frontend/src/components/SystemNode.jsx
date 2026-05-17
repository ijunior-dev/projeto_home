import { Handle, Position } from 'reactflow'

const STATUS_COLOR = {
  online: '#22c55e',
  offline: '#ef4444',
  unknown: '#6b7280',
}

const STATUS_LABEL = {
  online: 'online',
  offline: 'offline',
  unknown: 'desconhecido',
}

export default function SystemNode({ data }) {
  const color = STATUS_COLOR[data.status] ?? STATUS_COLOR.unknown

  return (
    <div
      style={{
        background: '#0f172a',
        border: `2px solid ${color}`,
        borderRadius: '10px',
        padding: '12px 16px',
        minWidth: '175px',
        color: '#f1f5f9',
        fontFamily: "'Courier New', monospace",
        boxShadow: `0 0 14px ${color}2a`,
        transition: 'border-color 0.4s ease, box-shadow 0.4s ease',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: color, border: 'none', width: 8, height: 8 }}
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
        <span style={{ fontSize: '18px' }}>{data.icon}</span>
        <span style={{ fontWeight: '700', fontSize: '13px', letterSpacing: '0.02em', flex: 1 }}>
          {data.label}
        </span>
        <span
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: color,
            flexShrink: 0,
            boxShadow: `0 0 8px ${color}`,
          }}
        />
      </div>

      <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '2px' }}>
        {data.subtitle}
      </div>

      {data.port && (
        <div style={{ fontSize: '10px', color: '#475569' }}>porta :{data.port}</div>
      )}

      <div
        style={{
          fontSize: '10px',
          color: color,
          marginTop: '7px',
          fontWeight: '600',
          textTransform: 'uppercase',
          letterSpacing: '0.07em',
        }}
      >
        ● {STATUS_LABEL[data.status] ?? 'desconhecido'}
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: color, border: 'none', width: 8, height: 8 }}
      />
    </div>
  )
}
