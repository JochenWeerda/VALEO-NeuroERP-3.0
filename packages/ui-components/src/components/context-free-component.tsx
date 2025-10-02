// packages/ui-components/src/hooks/use-service.ts
// import { serviceLocator } from '@valero-neuroerp/utilities';

export const useService = <T,>(key: string): T => {
  // return serviceLocator.get<T>(key);
  throw new Error('Service locator not available - module resolution issue');
};

export const useServiceFactory = <T,>(key: string, factory: () => T): T => {
  // if (!serviceLocator.has(key)) {
  //   serviceLocator.registerFactory(key, factory);
  // }
  // return serviceLocator.get<T>(key);
  throw new Error('Service locator not available - module resolution issue');
};
