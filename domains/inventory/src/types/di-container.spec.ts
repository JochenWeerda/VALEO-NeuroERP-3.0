import { DIContainer } from './di-container';

describe('DIContainer', () => {
  it('registers and resolves services by key', () => {
    const service = { name: 'inventory-service' };

    DIContainer.register('inventory-service-test', service, {
      singleton: true,
      dependencies: [],
    });

    expect(DIContainer.resolve('inventory-service-test')).toBe(service);
  });

  it('fails closed for unknown services', () => {
    expect(() => DIContainer.resolve('missing-service-test')).toThrow(
      'Service missing-service-test not found in DI container',
    );
  });
});
