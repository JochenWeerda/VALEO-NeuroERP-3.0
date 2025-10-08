/**
 * VALEO NeuroERP 3.0 - Business Rules Engine Tests
 */

import { BusinessRule } from '../business-rule';
import { RuleRegistry } from '../rule-registry';
import { ConflictDetector } from '../conflict-detection';
import { BusinessLogicOrchestrator } from '../business-logic-orchestrator';

// Test context
interface TestContext {
  value: number;
  messages: string[];
  isValid: boolean;
}

// Test rule
class TestRule extends BusinessRule<TestContext> {
  name = 'TestRule';
  description = 'A test rule';
  priority = 10;

  applies(context: TestContext): boolean {
    return context.value > 5;
  }

  execute(context: TestContext): void {
    context.messages.push('TestRule executed');
    context.value += 1;
  }
}

// Another test rule
class AnotherTestRule extends BusinessRule<TestContext> {
  name = 'AnotherTestRule';
  description = 'Another test rule';
  priority = 20;

  applies(context: TestContext): boolean {
    return context.value > 10;
  }

  execute(context: TestContext): void {
    context.messages.push('AnotherTestRule executed');
    context.value += 2;
  }
}

describe('Business Rules Engine', () => {
  beforeEach(() => {
    RuleRegistry.clear();
  });

  describe('Rule Registry', () => {
    it('should register and retrieve rules', () => {
      const rule = new TestRule();
      RuleRegistry.registerRule('test', rule);

      const rules = RuleRegistry.getRulesForDomain('test');
      expect(rules).toHaveLength(1);
      expect(rules[0].name).toBe('TestRule');
    });

    it('should sort rules by priority', () => {
      const rule1 = new TestRule();
      rule1.priority = 20;

      const rule2 = new AnotherTestRule();
      rule2.priority = 10;

      RuleRegistry.registerRule('test', rule1);
      RuleRegistry.registerRule('test', rule2);

      const rules = RuleRegistry.getRulesForDomain('test');
      expect(rules[0].priority).toBeLessThanOrEqual(rules[1].priority);
    });
  });

  describe('Conflict Detection', () => {
    it('should detect duplicate rule names', () => {
      const rule1 = new TestRule();
      const rule2 = new TestRule(); // Same name

      RuleRegistry.registerRule('test', rule1);
      RuleRegistry.registerRule('test', rule2);

      const rules = RuleRegistry.getRulesForDomain('test');
      const conflicts = ConflictDetector.detectConflicts(rules, 'test');

      expect(conflicts.some(c => c.severity === 'error')).toBe(true);
    });
  });

  describe('Business Logic Orchestrator', () => {
    it('should execute applicable rules', async () => {
      const rule1 = new TestRule();
      const rule2 = new AnotherTestRule();

      RuleRegistry.registerRule('test', rule1);
      RuleRegistry.registerRule('test', rule2);

      const orchestrator = new BusinessLogicOrchestrator('test');
      const context: TestContext = {
        value: 7, // Will trigger first rule
        messages: [],
        isValid: true
      };

      const result = await orchestrator.execute(context);

      expect(result.success).toBe(true);
      expect(result.executedRules).toContain('TestRule');
      expect(result.context.value).toBe(8); // 7 + 1
      expect(result.context.messages).toContain('TestRule executed');
    });

    it('should not execute inapplicable rules', async () => {
      const rule = new TestRule();
      RuleRegistry.registerRule('test', rule);

      const orchestrator = new BusinessLogicOrchestrator('test');
      const context: TestContext = {
        value: 3, // Won't trigger rule (value <= 5)
        messages: [],
        isValid: true
      };

      const result = await orchestrator.execute(context);

      expect(result.success).toBe(true);
      expect(result.executedRules).toHaveLength(0);
      expect(result.context.value).toBe(3);
    });
  });
});