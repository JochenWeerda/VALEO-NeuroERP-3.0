/**
 * VALEO NeuroERP 3.0 - Business Logic Orchestrator
 *
 * Orchestrates the execution of business rules with conflict detection and audit trail
 */

import { RuleRegistry } from './rule-registry';
import { ConflictAnalysisResult, ConflictDetector, RuleConflict } from './conflict-detection';
import { IBusinessRule } from './business-rule';

export interface ExecutionResult<TContext> {
  context: TContext;
  executedRules: string[];
  conflicts: RuleConflict[];
  executionTime: number;
  success: boolean;
  error?: string;
}

export interface OrchestratorOptions {
  failOnConflicts: boolean;
  logExecution: boolean;
  maxExecutionTime: number; // milliseconds
}

const DEFAULT_OPTIONS: OrchestratorOptions = {
  failOnConflicts: false,
  logExecution: true,
  maxExecutionTime: 5000
};

export class BusinessLogicOrchestrator {
  private readonly domain: string;
  private options: OrchestratorOptions;

  constructor(domain: string, options: Partial<OrchestratorOptions> = {}) {
    this.domain = domain;
    this.options = { ...DEFAULT_OPTIONS, ...options };
  }

  /**
   * Legacy method for backward compatibility
   * @deprecated Use execute() instead
   */
  public async executeBusinessLogic<TContext>(domain: string, context: TContext): Promise<ExecutionResult<TContext>> {
    const tempOrchestrator = new BusinessLogicOrchestrator(domain, this.options);
    return tempOrchestrator.execute(context);
  }

  /**
   * Legacy method for backward compatibility
   * @deprecated Use RuleRegistry.registerRule() instead
   */
  public registerRule<TContext>(domain: string, rule: IBusinessRule<TContext>): void {
    RuleRegistry.registerRule(domain, rule);
  }

  /**
   * Execute business rules for the given context
   */
  public async execute<TContext>(context: TContext): Promise<ExecutionResult<TContext>> {
    const startTime = Date.now();
    const executedRules: string[] = [];

    try {
      // 1. Get rules for this domain
      const rules = RuleRegistry.getRulesForDomain<TContext>(this.domain);

      if (this.options.logExecution) {
        console.info(`[BusinessLogicOrchestrator] Executing ${rules.length} rules for domain "${this.domain}"`);
      }

      // 2. Conflict Detection
      const conflicts = ConflictDetector.detectConflicts(rules, this.domain);
      const conflictAnalysis = ConflictDetector.analyzeConflicts(conflicts);

      if (this.options.logExecution) {
        console.info(`[BusinessLogicOrchestrator] Conflict analysis: ${conflictAnalysis.summary}`);
      }

      // 3. Fail if there are errors and failOnConflicts is true
      if (this.options.failOnConflicts && conflictAnalysis.hasErrors) {
        return {
          context,
          executedRules: [],
          conflicts,
          executionTime: Date.now() - startTime,
          success: false,
          error: `Rule conflicts detected: ${conflictAnalysis.summary}`
        };
      }

      // 4. Execute rules in priority order
      for (const rule of rules) {
        // Check execution time limit
        if (Date.now() - startTime > this.options.maxExecutionTime) {
          return {
            context,
            executedRules,
            conflicts,
            executionTime: Date.now() - startTime,
            success: false,
            error: `Execution timeout after ${this.options.maxExecutionTime}ms`
          };
        }

        // Check if rule should be executed
        const shouldExecute = rule.applies ? rule.applies(context) : true;

        if (shouldExecute) {
          if (this.options.logExecution) {
            console.info(`[BusinessLogicOrchestrator] Executing rule: ${rule.name} (Priority: ${rule.priority})`);
          }

          try {
            // Use validation method if available, otherwise use execute method
            if (rule.validate) {
              const validationResult = await rule.validate(context);
              if (!validationResult.isValid) {
                return {
                  context,
                  executedRules,
                  conflicts,
                  executionTime: Date.now() - startTime,
                  success: false,
                  error: `Validation failed: ${validationResult.errors.map(e => e.message).join(', ')}`
                };
              }
            } else if (rule.execute) {
              await rule.execute(context);
            }
            executedRules.push(rule.name);
          } catch (error) {
            console.error(`[BusinessLogicOrchestrator] Error executing rule ${rule.name}:`, error);
            return {
              context,
              executedRules,
              conflicts,
              executionTime: Date.now() - startTime,
              success: false,
              error: `Rule execution failed: ${rule.name} - ${String(error)}`
            };
          }
        }
      }

      const executionTime = Date.now() - startTime;

      if (this.options.logExecution) {
        console.info(`[BusinessLogicOrchestrator] Execution completed successfully in ${executionTime}ms. Executed ${executedRules.length} rules.`);
      }

      return {
        context,
        executedRules,
        conflicts,
        executionTime,
        success: true
      };

    } catch (error) {
      console.error(`[BusinessLogicOrchestrator] Unexpected error:`, error);
      return {
        context,
        executedRules,
        conflicts: [],
        executionTime: Date.now() - startTime,
        success: false,
        error: `Unexpected error: ${String(error)}`
      };
    }
  }

  /**
   * Get rules for this domain (for inspection/debugging)
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public getRules(): IBusinessRule<any>[] {
    return RuleRegistry.getRulesForDomain(this.domain);
  }

  /**
   * Analyze conflicts without executing rules
   */
  public analyzeConflicts(): ConflictAnalysisResult {
    const rules = RuleRegistry.getRulesForDomain(this.domain);
    const conflicts = ConflictDetector.detectConflicts(rules, this.domain);
    return ConflictDetector.analyzeConflicts(conflicts);
  }

  /**
   * Update orchestrator options
   */
  public updateOptions(options: Partial<OrchestratorOptions>): void {
    this.options = { ...this.options, ...options };
  }
}