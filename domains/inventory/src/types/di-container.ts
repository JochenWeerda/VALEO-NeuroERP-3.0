export class DIContainer {
  private static readonly services = new Map<string, unknown>();

  static register<T>(
    key: string,
    service: T,
    _options?: { singleton?: boolean; dependencies?: string[] },
  ): void {
    this.services.set(key, service);
  }

  static resolve<T>(key: string): T {
    const service = this.services.get(key);
    if (service === undefined) {
      throw new Error(`Service ${key} not found in DI container`);
    }
    return service as T;
  }
}
