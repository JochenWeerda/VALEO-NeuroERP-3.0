/**
 * Tree View Component
 * Hierarchical tree display for accounts, categories, etc.
 */

import React, { useState } from 'react'
import { ChevronRight, ChevronDown, Folder, FolderOpen } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface TreeNode {
  id: string
  label: string
  children?: TreeNode[]
  data?: any
}

interface TreeViewProps {
  nodes: TreeNode[]
  onNodeClick?: (node: TreeNode) => void
  selectedNodeId?: string
  defaultExpanded?: string[]
  className?: string
}

export function TreeView({
  nodes,
  onNodeClick,
  selectedNodeId,
  defaultExpanded = [],
  className,
}: TreeViewProps): JSX.Element {
  const [expanded, setExpanded] = useState<Set<string>>(new Set(defaultExpanded))

  const toggleExpanded = (nodeId: string) => {
    const newExpanded = new Set(expanded)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpanded(newExpanded)
  }

  const renderNode = (node: TreeNode, level: number = 0): JSX.Element => {
    const hasChildren = node.children && node.children.length > 0
    const isExpanded = expanded.has(node.id)
    const isSelected = selectedNodeId === node.id

    return (
      <div key={node.id}>
        <div
          className={cn(
            'flex items-center gap-2 py-1 px-2 rounded hover:bg-accent cursor-pointer',
            isSelected && 'bg-accent',
            className
          )}
          style={{ paddingLeft: `${level * 1.5}rem` }}
          onClick={() => {
            if (hasChildren) {
              toggleExpanded(node.id)
            }
            onNodeClick?.(node)
          }}
        >
          {hasChildren ? (
            <button
              className="p-0.5 hover:bg-accent rounded"
              onClick={(e) => {
                e.stopPropagation()
                toggleExpanded(node.id)
              }}
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
          ) : (
            <div className="w-5" />
          )}
          {hasChildren && (isExpanded ? <FolderOpen className="h-4 w-4" /> : <Folder className="h-4 w-4" />)}
          <span className="flex-1 text-sm">{node.label}</span>
        </div>
        {hasChildren && isExpanded && (
          <div>{node.children!.map((child) => renderNode(child, level + 1))}</div>
        )}
      </div>
    )
  }

  return <div className="space-y-1">{nodes.map((node) => renderNode(node))}</div>
}

