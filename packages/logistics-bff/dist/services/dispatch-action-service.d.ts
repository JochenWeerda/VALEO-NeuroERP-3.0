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
export declare class DispatchActionService {
    private pendingActions;
    private quickActions;
    createAction(action: Omit<DispatchAction, 'id' | 'timestamp' | 'status'>): DispatchAction;
    getPendingActions(): DispatchAction[];
    approveAction(actionId: string, approvedBy: string): boolean;
    rejectAction(actionId: string, reason: string): boolean;
    getQuickActions(): QuickAction[];
    executeQuickAction(actionId: string, shipmentId: string, userId: string): DispatchAction | null;
    private generateId;
}
//# sourceMappingURL=dispatch-action-service.d.ts.map