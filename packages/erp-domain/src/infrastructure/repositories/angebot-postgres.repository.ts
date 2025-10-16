import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { Angebot } from '../../core/entities/angebot.entity'
import { AngebotRepository } from '../../core/repositories/angebot.repository'
import { AngebotStatus } from '../../core/entities/angebot.entity'

@injectable()
export class AngebotPostgresRepository implements AngebotRepository {
  constructor(private prisma: PrismaClient) {}

  async save(angebot: Angebot): Promise<Angebot> {
    const data = {
      id: angebot.id,
      angebotNummer: angebot.angebotNummer,
      anfrageId: angebot.anfrageId,
      lieferantId: angebot.lieferantId,
      artikel: angebot.artikel,
      menge: angebot.menge,
      einheit: angebot.einheit,
      preis: angebot.preis,
      waehrung: angebot.waehrung,
      lieferzeit: angebot.lieferzeit,
      gueltigBis: angebot.gueltigBis,
      status: angebot.status,
      mindestabnahme: angebot.mindestabnahme,
      zahlungsbedingungen: angebot.zahlungsbedingungen,
      incoterms: angebot.incoterms,
      bemerkungen: angebot.bemerkungen,
      tenantId: angebot.tenantId,
      version: angebot.version,
      createdAt: angebot.createdAt,
      updatedAt: angebot.updatedAt,
      deletedAt: angebot.deletedAt
    }

    const saved = await this.prisma.angebot.upsert({
      where: { id: angebot.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<Angebot | null> {
    const result = await this.prisma.angebot.findFirst({
      where: {
        id,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByNummer(nummer: string, tenantId: string): Promise<Angebot | null> {
    const result = await this.prisma.angebot.findFirst({
      where: {
        angebotNummer: nummer,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByTenant(tenantId: string, options?: {
    status?: AngebotStatus
    lieferantId?: string
    anfrageId?: string
    limit?: number
    offset?: number
  }): Promise<Angebot[]> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (options?.status) where.status = options.status
    if (options?.lieferantId) where.lieferantId = options.lieferantId
    if (options?.anfrageId) where.anfrageId = options.anfrageId

    const results = await this.prisma.angebot.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findAbgelaufene(tenantId: string): Promise<Angebot[]> {
    const results = await this.prisma.angebot.findMany({
      where: {
        tenantId,
        gueltigBis: { lt: new Date() },
        status: { not: AngebotStatus.ABGELEHNT },
        deletedAt: null
      },
      orderBy: { gueltigBis: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async findByAnfrage(anfrageId: string, tenantId: string): Promise<Angebot[]> {
    const results = await this.prisma.angebot.findMany({
      where: {
        anfrageId,
        tenantId,
        deletedAt: null
      },
      orderBy: { createdAt: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async update(angebot: Angebot): Promise<Angebot> {
    const data = {
      angebotNummer: angebot.angebotNummer,
      anfrageId: angebot.anfrageId,
      lieferantId: angebot.lieferantId,
      artikel: angebot.artikel,
      menge: angebot.menge,
      einheit: angebot.einheit,
      preis: angebot.preis,
      waehrung: angebot.waehrung,
      lieferzeit: angebot.lieferzeit,
      gueltigBis: angebot.gueltigBis,
      status: angebot.status,
      mindestabnahme: angebot.mindestabnahme,
      zahlungsbedingungen: angebot.zahlungsbedingungen,
      incoterms: angebot.incoterms,
      bemerkungen: angebot.bemerkungen,
      version: angebot.version,
      updatedAt: angebot.updatedAt,
      deletedAt: angebot.deletedAt
    }

    const updated = await this.prisma.angebot.update({
      where: { id: angebot.id },
      data
    })

    return this.mapToEntity(updated)
  }

  async delete(id: string, tenantId: string): Promise<void> {
    await this.prisma.angebot.update({
      where: { id },
      data: { deletedAt: new Date() }
    })
  }

  async countByTenant(tenantId: string, status?: AngebotStatus): Promise<number> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (status) where.status = status

    return this.prisma.angebot.count({ where })
  }

  private mapToEntity(data: any): Angebot {
    return new Angebot(
      data.id,
      data.angebotNummer,
      data.anfrageId,
      data.lieferantId,
      data.artikel,
      data.menge,
      data.einheit,
      data.preis,
      data.waehrung,
      data.lieferzeit,
      data.gueltigBis,
      data.status,
      data.tenantId,
      data.mindestabnahme,
      data.zahlungsbedingungen,
      data.incoterms,
      data.bemerkungen,
      data.version,
      data.createdAt,
      data.updatedAt,
      data.deletedAt
    )
  }
}