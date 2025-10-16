import { Request } from 'express'

declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string
        tenantId: string
        email?: string
        roles?: string[]
        [key: string]: any
      }
      tenantId?: string
    }
  }
}

export {}

