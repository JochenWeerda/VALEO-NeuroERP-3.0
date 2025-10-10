/**
 * VALEO NeuroERP 3.0 - Conflict Detection
 *
 * Detects conflicts between business rules to prevent inconsistent behavior
 */

export interface RuleConflict {
  rule1: string;
  rule2: string;
  description: string;
  severity: 'warning' | 'error';
  domain: string;
}

export interface ConflictAnalysisResult {
  conflicts: RuleConflict[];
  hasErrors: boolean;
  hasWarnings: boolean;
  summary: string;
}

export class ConflictDetector {
  /**
   * Detect conflicts in a set of business rules
   */
  public static detectConflicts<_TContext = unknown>(
    rules: Array<{ name: string; description: string; priority: number }>,
    domain: string
  ): RuleConflict[] {
    const conflicts: RuleConflict[] = [];

    // 1. Check for duplicate rule names
    const ruleNames = new Set<string>();
    rules.forEach(rule => {
      if (ruleNames.has(rule.name)) {
        conflicts.push({
          rule1: rule.name,
          rule2: rule.name,
          description: `Duplicate rule name detected: "${rule.name}". This might lead to unexpected behavior.`,
          severity: 'error',
          domain
        });
      }
      ruleNames.add(rule.name);
    });

    // 2. Check for conflicting priorities (same priority might indicate oversight)
    const priorityGroups = new Map<number, string[]>();
    rules.forEach(rule => {
      if (!priorityGroups.has(rule.priority)) {
        priorityGroups.set(rule.priority, []);
      }
      const group = priorityGroups.get(rule.priority);
      if (group !== undefined) {
        group.push(rule.name);
      }
    });

    priorityGroups.forEach((ruleNames, priority) => {
      if (ruleNames.length > 1) {
        conflicts.push({
          rule1: ruleNames[0],
          rule2: ruleNames[1],
          description: `Multiple rules with same priority (${priority}): ${ruleNames.join(', ')}. Consider adjusting priorities.`,
          severity: 'warning',
          domain
        });
      }
    });

    // 3. Check for potentially conflicting descriptions (simple heuristic)
    for (let i = 0; i < rules.length; i++) {
      for (let j = i + 1; j < rules.length; j++) {
        const rule1 = rules[i];
        const rule2 = rules[j];

        // Check if descriptions contain opposite keywords
        const desc1 = rule1.description.toLowerCase();
        const desc2 = rule2.description.toLowerCase();

        const positiveKeywords = ['allow', 'enable', 'permit', 'accept', 'valid'];
        const negativeKeywords = ['deny', 'disable', 'reject', 'invalid', 'block'];

        const hasPositive1 = positiveKeywords.some(k => desc1.includes(k));
        const hasNegative1 = negativeKeywords.some(k => desc1.includes(k));
        const hasPositive2 = positiveKeywords.some(k => desc2.includes(k));
        const hasNegative2 = negativeKeywords.some(k => desc2.includes(k));

        if ((hasPositive1 && hasNegative2) || (hasNegative1 && hasPositive2)) {
          conflicts.push({
            rule1: rule1.name,
            rule2: rule2.name,
            description: `Potential conflict detected between "${rule1.name}" and "${rule2.name}" based on rule descriptions.`,
            severity: 'warning',
            domain
          });
        }
      }
    }

    return conflicts;
  }

  /**
   * Analyze conflicts and provide a summary
   */
  public static analyzeConflicts(conflicts: RuleConflict[]): ConflictAnalysisResult {
    const hasErrors = conflicts.some(c => c.severity === 'error');
    const hasWarnings = conflicts.some(c => c.severity === 'warning');

    let summary = `Found ${conflicts.length} conflicts: `;
    summary += `${conflicts.filter(c => c.severity === 'error').length} errors, `;
    summary += `${conflicts.filter(c => c.severity === 'warning').length} warnings`;

    return {
      conflicts,
      hasErrors,
      hasWarnings,
      summary
    };
  }

  /**
   * Filter conflicts by severity
   */
  public static filterBySeverity(conflicts: RuleConflict[], severity: 'warning' | 'error'): RuleConflict[] {
    return conflicts.filter(c => c.severity === severity);
  }

  /**
   * Get conflicts for a specific domain
   */
  public static getConflictsForDomain(conflicts: RuleConflict[], domain: string): RuleConflict[] {
    return conflicts.filter(c => c.domain === domain);
  }
}