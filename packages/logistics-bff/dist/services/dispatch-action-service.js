"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DispatchActionService = void 0;
class DispatchActionService {
    constructor() {
        this.pendingActions = [];
        this.quickActions = [
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
    }
    // Create dispatch action
    createAction(action) {
        const newAction = {
            ...action,
            id: this.generateId(),
            timestamp: new Date().toISOString(),
            status: 'pending'
        };
        this.pendingActions.push(newAction);
        return newAction;
    }
    // Get pending actions
    getPendingActions() {
        return [...this.pendingActions];
    }
    // Approve action
    approveAction(actionId, approvedBy) {
        const action = this.pendingActions.find(a => a.id === actionId);
        if (action) {
            action.status = 'approved';
            // TODO: Execute the action via domain service
            return true;
        }
        return false;
    }
    // Reject action
    rejectAction(actionId, reason) {
        const action = this.pendingActions.find(a => a.id === actionId);
        if (action) {
            action.status = 'rejected';
            return true;
        }
        return false;
    }
    // Get quick actions for UI
    getQuickActions() {
        return [...this.quickActions];
    }
    // Execute quick action
    executeQuickAction(actionId, shipmentId, userId) {
        const quickAction = this.quickActions.find(qa => qa.id === actionId);
        if (!quickAction)
            return null;
        let actionType;
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
    generateId() {
        return 'action_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
}
exports.DispatchActionService = DispatchActionService;
//# sourceMappingURL=dispatch-action-service.js.map