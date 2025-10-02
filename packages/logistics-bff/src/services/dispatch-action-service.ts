export interface DispatchAction {
  id: string;
  type: 'reassign' | 'reroute' | 'priority_change' | 'emergency_stop' | 'break_request';
  shipmentId: string;
  driverId?: string;
  vehicleId?: string;
  reason: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  requestedBy: string;
  timestamp: string;
  status: 'pending' | 'approved' | 'rejected' | 'executed';
}

export interface QuickAction {
  id: string;
  label: string;
  icon: string;
  color: string;
  shortcut: string;
  description: string;
}

export class DispatchActionService {
  private pendingActions: DispatchAction[] = [];
  private quickActions: QuickAction[] = [
    {
      id: 'emergency_stop',
      label: 'Emergency Stop',
      icon: '⛔',
      color: 'red',
      shortcut: 'Ctrl+E',
      description: 'Immediately stop vehicle and alert emergency services'
    },
    {
      id: 'reroute',
      label: 'Reroute',
      icon: '🔄',
      color: 'blue',
      shortcut: 'Ctrl+R',
      description: 'Calculate alternative route due to traffic or issues'
    },
    {
      id: 'reassign',
      label: 'Reassign',
      icon: '🔄',
      color: 'orange',
      shortcut: 'Ctrl+A',
      description: 'Reassign driver or vehicle to different shipment'
    },
    {
      id: 'priority_up',
      label: 'Priority Up',
      icon: '⬆️',
      color: 'purple',
      shortcut: 'Ctrl+P',
      description: 'Increase shipment priority level'
    }
  ];

  // Create dispatch action
  createAction(action: Omit<DispatchAction, 'id' | 'timestamp' | 'status'>): DispatchAction {
    const newAction: DispatchAction = {
      ...action,
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      status: 'pending'
    };

    this.pendingActions.push(newAction);
    return newAction;
  }

  // Get pending actions
  getPendingActions(): DispatchAction[] {
    return [...this.pendingActions];
  }

  // Approve action
  approveAction(actionId: string, approvedBy: string): boolean {
    const action = this.pendingActions.find(a => a.id === actionId);
    if (action) {
      action.status = 'approved';
      // TODO: Execute the action via domain service
      return true;
    }
    return false;
  }

  // Reject action
  rejectAction(actionId: string, reason: string): boolean {
    const action = this.pendingActions.find(a => a.id === actionId);
    if (action) {
      action.status = 'rejected';
      return true;
    }
    return false;
  }

  // Get quick actions for UI
  getQuickActions(): QuickAction[] {
    return [...this.quickActions];
  }

  // Execute quick action
  executeQuickAction(actionId: string, shipmentId: string, userId: string): DispatchAction | null {
    const quickAction = this.quickActions.find(qa => qa.id === actionId);
    if (!quickAction) return null;

    let actionType: DispatchAction['type'];
    switch (actionId) {
      case 'emergency_stop':
        actionType = 'emergency_stop';
        break;
      case 'reroute':
        actionType = 'reroute';
        break;
      case 'reassign':
        actionType = 'reassign';
        break;
      case 'priority_up':
        actionType = 'priority_change';
        break;
      default:
        return null;
    }

    return this.createAction({
      type: actionType,
      shipmentId,
      reason: `Quick action: ${quickAction.label}`,
      priority: actionId === 'emergency_stop' ? 'critical' : 'high',
      requestedBy: userId
    });
  }

  private generateId(): string {
    return 'action_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
}