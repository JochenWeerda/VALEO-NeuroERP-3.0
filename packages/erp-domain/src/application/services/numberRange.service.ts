import { injectable } from 'inversify'

@injectable()
export class NumberRangeService {
  async generateNumber(prefix: string, tenantId: string): Promise<string> {
    const safeTenant = tenantId.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 12) || 'tenant'
    return `${prefix}-${safeTenant}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
  }
}
