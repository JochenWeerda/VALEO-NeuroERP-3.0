import { LabelEvaluateInput, LabelEvaluationResult } from '../entities/label';
export declare function evaluateLabel(tenantId: string, input: LabelEvaluateInput): Promise<LabelEvaluationResult>;
export declare function createOrUpdateLabel(tenantId: string, input: LabelEvaluateInput, evaluation: LabelEvaluationResult, userId: string): Promise<any>;
//# sourceMappingURL=label-evaluation-service.d.ts.map