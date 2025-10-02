// packages/utilities/src/di-container.ts
export interface DependencyDefinition {
  key: string;
  factory: () => any;
  dependencies: string[];
  singleton: boolean;
  lazy: boolean;
  scope: 'singleton' | 'transient' | 'scoped';
}

export class DIContainer {
  private dependencies = new Map<string, DependencyDefinition>();
  private singletons = new Map<string, any>();
  private scopedInstances = new Map<string, Map<string, any>>();
  private currentScope: string | null = null;

  register<T>(
    key: string,
    factory: () => T,
    options: {
      dependencies?: string[];
      singleton?: boolean;
      lazy?: boolean;
      scope?: 'singleton' | 'transient' | 'scoped';
    } = {}
  ): void {
    const definition: DependencyDefinition = {
      key,
      factory,
      dependencies: options.dependencies || [],
      singleton: options.singleton ?? true,
      lazy: options.lazy ?? false,
      scope: options.scope ?? 'singleton'
    };

    this.dependencies.set(key, definition);

    if (definition.singleton) {
      this.singletons.set(key, null);
    }
  }

  async resolve<T>(key: string): Promise<T> {
    const definition = this.dependencies.get(key);
    if (!definition) {
      throw new Error(`Dependency ${key} not registered`);
    }

    // Check if already resolved in current scope
    if (definition.scope === 'scoped' && this.currentScope) {
      const scopedInstances = this.scopedInstances.get(this.currentScope);
      if (scopedInstances && scopedInstances.has(key)) {
        return scopedInstances.get(key);
      }
    }

    // Resolve dependencies first
    const resolvedDependencies = await this.resolveDependencies(definition.dependencies);

    // Create instance
    const instance = definition.factory.apply(null, resolvedDependencies as any);

    // Store based on scope
    if (definition.scope === 'singleton') {
      this.singletons.set(key, instance);
    } else if (definition.scope === 'scoped' && this.currentScope) {
      if (!this.scopedInstances.has(this.currentScope)) {
        this.scopedInstances.set(this.currentScope, new Map());
      }
      this.scopedInstances.get(this.currentScope)!.set(key, instance);
    }

    return instance;
  }

  private async resolveDependencies(dependencies: string[]): Promise<any[]> {
    const resolved: any[] = [];
    
    for (const dep of dependencies) {
      const resolvedDep = await this.resolve(dep);
      resolved.push(resolvedDep);
    }
    
    return resolved;
  }

  // Create a new scope
  createScope(scopeId: string): void {
    this.currentScope = scopeId;
  }

  // End current scope
  endScope(): void {
    this.currentScope = null;
  }

  // Clear scoped instances
  clearScope(scopeId: string): void {
    this.scopedInstances.delete(scopeId);
  }

  // Circular dependency detection
  detectCircularDependency(key: string, visited: Set<string> = new Set()): boolean {
    if (visited.has(key)) {
      return true;
    }

    visited.add(key);
    const definition = this.dependencies.get(key);
    
    if (definition) {
      for (const dep of definition.dependencies) {
        if (this.detectCircularDependency(dep, new Set(visited))) {
          return true;
        }
      }
    }

    visited.delete(key);
    return false;
  }
}

// Global DI Container
export const container = new DIContainer();
