"use strict";
// Services and Infrastructure Types
Object.defineProperty(exports, "__esModule", { value: true });
exports.metricsService = exports.ServiceLocator = void 0;
class ServiceLocator {
    static instance;
    services = new Map();
    static getInstance() {
        if (!ServiceLocator.instance) {
            ServiceLocator.instance = new ServiceLocator();
        }
        return ServiceLocator.instance;
    }
    registerInstance(token, instance) {
        this.services.set(token, instance);
    }
    registerFactory(token, factory) {
        this.services.set(token, factory);
    }
    resolve(token) {
        const service = this.services.get(token);
        if (!service) {
            throw new Error(`Service with token '${token}' not found`);
        }
        return typeof service === 'function' ? service() : service;
    }
    has(token) {
        return this.services.has(token);
    }
    unregister(token) {
        this.services.delete(token);
    }
}
exports.ServiceLocator = ServiceLocator;
exports.metricsService = {
    incrementCounter(name, labels) {
        console.log(`[METRICS] Counter ${name} incremented`, labels);
    },
    recordGauge(name, value, labels) {
        console.log(`[METRICS] Gauge ${name} recorded: ${value}`, labels);
    },
    recordHistogram(name, value, labels) {
        console.log(`[METRICS] Histogram ${name} recorded: ${value}`, labels);
    },
};
