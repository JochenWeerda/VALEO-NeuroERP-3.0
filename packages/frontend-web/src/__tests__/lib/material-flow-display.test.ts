import { describe, expect, it } from 'vitest'

import {
  agriMaterialFlowApiToReactFlowEdges,
  agriMaterialFlowApiToReactFlowNodes,
  flowEdgeStatusGermanLabel,
  flowNodeStatusBorderClass,
  flowNodeStatusGermanLabel,
  qsStatusGermanLabel,
  qsStatusToBadgeVariant,
} from '@/lib/material-flow-display'

describe('material-flow-display', () => {
  it('maps qs_status to badge variant', () => {
    expect(qsStatusToBadgeVariant('frei')).toBe('secondary')
    expect(qsStatusToBadgeVariant('gesperrt')).toBe('destructive')
    expect(qsStatusToBadgeVariant('in_pruefung')).toBe('outline')
  })

  it('maps qs_status to German labels', () => {
    expect(qsStatusGermanLabel('in_pruefung')).toBe('in Prüfung')
    expect(qsStatusGermanLabel(undefined)).toBe('frei')
  })

  it('maps node status to labels and border classes', () => {
    expect(flowNodeStatusGermanLabel('maintenance')).toBe('Wartung')
    expect(flowNodeStatusBorderClass('blocked')).toContain('red')
    expect(flowNodeStatusBorderClass('active')).toContain('emerald')
  })

  it('maps edge status to German labels', () => {
    expect(flowEdgeStatusGermanLabel('open')).toBe('offen')
    expect(flowEdgeStatusGermanLabel('blocked')).toBe('gesperrt')
  })

  it('maps API nodes to React Flow with layout or grid fallback', () => {
    const nodes = agriMaterialFlowApiToReactFlowNodes([
      { id: 'x1', code: 'B', name: 'n2', node_type: 'scale', status: 'active', layout_x: 10, layout_y: 20 },
      { id: 'x2', code: 'A', name: 'n1', node_type: 'intake', status: 'blocked' },
    ])
    expect(nodes).toHaveLength(2)
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]))
    expect(byId.x1.position).toEqual({ x: 10, y: 20 })
    expect(byId.x2.type).toBe('mfProcess')
    expect(byId.x2.data?.status).toBe('blocked')
    expect(byId.x2.position.x).toBe(0)
    expect(byId.x2.position.y).toBe(0)
  })

  it('drops edges when an endpoint is missing from node set', () => {
    const nodeIds = new Set(['n1'])
    const edges = agriMaterialFlowApiToReactFlowEdges(
      [{ id: 'e1', from_node_id: 'n1', to_node_id: 'n2', status: 'open' }],
      nodeIds,
    )
    expect(edges).toHaveLength(0)
  })

  it('keeps edges when both endpoints exist', () => {
    const nodeIds = new Set(['n1', 'n2'])
    const edges = agriMaterialFlowApiToReactFlowEdges(
      [{ id: 'e1', from_node_id: 'n1', to_node_id: 'n2', status: 'open' }],
      nodeIds,
    )
    expect(edges).toHaveLength(1)
    expect(edges[0]?.source).toBe('n1')
    expect(edges[0]?.target).toBe('n2')
    expect(edges[0]?.animated).toBe(true)
  })
})
