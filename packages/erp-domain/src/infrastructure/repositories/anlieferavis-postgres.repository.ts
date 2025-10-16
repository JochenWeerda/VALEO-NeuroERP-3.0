import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { Anlieferavis } from '../../core/entities/anlieferavis.entity'
import { AnlieferavisRepository } from '../../core/repositories/anlieferavis.repository'
import { AnlieferavisStatus } from '../../core/entities/anlieferavis.entity'

@injectable()
export class AnlieferavisPostgresRepository implements AnlieferavisRepository {
  constructor(private prisma: PrismaClient) {}

  async save(avis: Anlieferavis): Promise<Anlieferavis> {
    const data = {
      id: avis.id,
      avisNummer: avis.avisNummer,
      bestellungId: avis.bestellungId,
      status: avis.status,
      geplantesAnlieferDatum: avis.geplantesAnlieferDatum,
      fahrzeug: avis.fahrzeug,
      positionen: avis.positionen,
      bemerkungen: avis.bemerkungen,
      tenantId: avis.tenantId,
      version: avis.version,
      createdAt: avis.createdAt,
      updatedAt: avis.updatedAt,
      deletedAt: avis.deletedAt
    }

    const saved = await this.prisma.anlieferavis.upsert({
      where: { id: avis.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<Anlieferavis | null> {
    const result = await this.prisma.anlieferavis.findFirst({
      where: {
        id,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByNummer(nummer: string, tenantId: string): Promise<Anlieferavis | null> {
    const result = await this.prisma.anlieferavis.findFirst({
      where: {
        avisNummer: nummer,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByBestellung(bestellungId: string, tenantId: string): Promise<Anlieferavis | null> {
    const result = await this.prisma.anlieferavis.findFirst({
      where: {
        bestellungId,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByTenant(tenantId: string, options?: {
    status?: AnlieferavisStatus
    bestellungId?: string
    limit?: number
    offset?: number
  }): Promise<Anlieferavis[]> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (options?.status) where.status = options.status
    if (options?.bestellungId) where.bestellungId = options.bestellungId

    const results = await this.prisma.anlieferavis.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findUeberfaellige(tenantId: string): Promise<Anlieferavis[]> {
    const results = await this.prisma.anlieferavis.findMany({
      where: {
        tenantId,
        geplantesAnlieferDatum: { lt: new Date() },
        status: { not: AnlieferavisStatus.STORNIERT },
        deletedAt: null
      },
      orderBy: { geplantesAnlieferDatum: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async update(avis: Anlieferavis): Promise<Anlieferavis> {
    const data = {
      avisNummer: avis.avisNummer,
      bestellungId: avis.bestellungId,
      status: avis.status,
      geplantesAnlieferDatum: avis.geplantesAnlieferDatum,
      fahrzeug: avis.fahrzeug,
      positionen: avis.positionen,
      bemerkungen: avis.bemerkungen,
      version: avis.version,
      updatedAt: avis.updatedAt,
      deletedAt: avis.deletedAt
    }

    const updated = await this.prisma.anlieferavis.update({
      where: { id: avis.id },
      data
    })

    return this.mapToEntity(updated)
  }

  async delete(id: string, tenantId: string): Promise<void> {
    await this.prisma.anlieferavis.update({
      where: { id },
      data: { deletedAt: new Date() }
    })
  }

  async countByTenant(tenantId: string, status?: AnlieferavisStatus): Promise<number> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (status) where.status = status

    return this.prisma.anlieferavis.count({ where })
  }

  private mapToEntity(data: any): Anlieferavis {
    return new Anlieferavis(
      data.id,
      data.avisNummer,
      data.bestellungId,
      data.status,
      data.geplantesAnlieferDatum,
      data.fahrzeug,
      data.positionen,
      data.tenantId,
      data.bemerkungen,
      data.version,
      data.createdAt,
      data.updatedAt,
      data.deletedAt
    )
  }
}