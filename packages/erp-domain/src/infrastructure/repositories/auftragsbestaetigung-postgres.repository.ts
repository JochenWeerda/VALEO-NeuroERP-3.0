import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { Auftragsbestaetigung } from '../../core/entities/auftragsbestaetigung.entity'
import { AuftragsbestaetigungRepository } from '../../core/repositories/auftragsbestaetigung.repository'
import { AuftragsbestaetigungStatus } from '../../core/entities/auftragsbestaetigung.entity'

@injectable()
export class AuftragsbestaetigungPostgresRepository implements AuftragsbestaetigungRepository {
  constructor(private prisma: PrismaClient) {}

  async save(ab: Auftragsbestaetigung): Promise<Auftragsbestaetigung> {
    const data = {
      id: ab.id,
      bestaetigungsNummer: ab.bestaetigungsNummer,
      bestellungId: ab.bestellungId,
      status: ab.status,
      bestaetigteTermine: ab.bestaetigteTermine,
      preisabweichungen: ab.preisabweichungen,
      bemerkungen: ab.bemerkungen,
      tenantId: ab.tenantId,
      version: ab.version,
      createdAt: ab.createdAt,
      updatedAt: ab.updatedAt,
      deletedAt: ab.deletedAt
    }

    const saved = await this.prisma.auftragsbestaetigung.upsert({
      where: { id: ab.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<Auftragsbestaetigung | null> {
    const result = await this.prisma.auftragsbestaetigung.findFirst({
      where: {
        id,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByNummer(nummer: string, tenantId: string): Promise<Auftragsbestaetigung | null> {
    const result = await this.prisma.auftragsbestaetigung.findFirst({
      where: {
        bestaetigungsNummer: nummer,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByBestellung(bestellungId: string, tenantId: string): Promise<Auftragsbestaetigung | null> {
    const result = await this.prisma.auftragsbestaetigung.findFirst({
      where: {
        bestellungId,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByTenant(tenantId: string, options?: {
    status?: AuftragsbestaetigungStatus
    bestellungId?: string
    limit?: number
    offset?: number
  }): Promise<Auftragsbestaetigung[]> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (options?.status) where.status = options.status
    if (options?.bestellungId) where.bestellungId = options.bestellungId

    const results = await this.prisma.auftragsbestaetigung.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findMitAbweichungen(tenantId: string): Promise<Auftragsbestaetigung[]> {
    const results = await this.prisma.auftragsbestaetigung.findMany({
      where: {
        tenantId,
        deletedAt: null,
        OR: [
          { bestaetigteTermine: { some: { abweichung: { not: null } } } } as any,
          { preisabweichungen: { some: { urspruenglicherPreis: { not: { equals: 'neuerPreis' } } } } } as any
        ]
      } as any,
      orderBy: { createdAt: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async update(ab: Auftragsbestaetigung): Promise<Auftragsbestaetigung> {
    const data = {
      bestaetigungsNummer: ab.bestaetigungsNummer,
      bestellungId: ab.bestellungId,
      status: ab.status,
      bestaetigteTermine: ab.bestaetigteTermine,
      preisabweichungen: ab.preisabweichungen,
      bemerkungen: ab.bemerkungen,
      version: ab.version,
      updatedAt: ab.updatedAt,
      deletedAt: ab.deletedAt
    }

    const updated = await this.prisma.auftragsbestaetigung.update({
      where: { id: ab.id },
      data
    })

    return this.mapToEntity(updated)
  }

  async delete(id: string, tenantId: string): Promise<void> {
    await this.prisma.auftragsbestaetigung.update({
      where: { id },
      data: { deletedAt: new Date() }
    })
  }

  async countByTenant(tenantId: string, status?: AuftragsbestaetigungStatus): Promise<number> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (status) where.status = status

    return this.prisma.auftragsbestaetigung.count({ where })
  }

  private mapToEntity(data: any): Auftragsbestaetigung {
    return new Auftragsbestaetigung(
      data.id,
      data.bestaetigungsNummer,
      data.bestellungId,
      data.status,
      data.bestaetigteTermine,
      data.preisabweichungen,
      data.tenantId,
      data.bemerkungen,
      data.version,
      data.createdAt,
      data.updatedAt,
      data.deletedAt
    )
  }
}