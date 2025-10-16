import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { Rechnungseingang } from '../../core/entities/rechnungseingang.entity'
import { RechnungseingangRepository } from '../../core/repositories/rechnungseingang.repository'
import { RechnungseingangStatus } from '../../core/entities/rechnungseingang.entity'

@injectable()
export class RechnungseingangPostgresRepository implements RechnungseingangRepository {
  constructor(private prisma: PrismaClient) {}

  async save(rechnung: Rechnungseingang): Promise<Rechnungseingang> {
    const data = {
      id: rechnung.id,
      rechnungsNummer: rechnung.rechnungsNummer,
      lieferantId: rechnung.lieferantId,
      bestellungId: rechnung.bestellungId,
      wareneingangId: rechnung.wareneingangId,
      rechnungsDatum: rechnung.rechnungsDatum,
      status: rechnung.status,
      bruttoBetrag: rechnung.bruttoBetrag,
      nettoBetrag: rechnung.nettoBetrag,
      steuerBetrag: rechnung.steuerBetrag,
      steuerSatz: rechnung.steuerSatz,
      skonto: rechnung.skonto,
      zahlungsziel: rechnung.zahlungsziel,
      positionen: rechnung.positionen,
      abweichungen: rechnung.abweichungen,
      bemerkungen: rechnung.bemerkungen,
      tenantId: rechnung.tenantId,
      version: rechnung.version,
      createdAt: rechnung.createdAt,
      updatedAt: rechnung.updatedAt,
      deletedAt: rechnung.deletedAt
    }

    const saved = await this.prisma.rechnungseingang.upsert({
      where: { id: rechnung.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<Rechnungseingang | null> {
    const result = await this.prisma.rechnungseingang.findFirst({
      where: {
        id,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByNummer(nummer: string, tenantId: string): Promise<Rechnungseingang | null> {
    const result = await this.prisma.rechnungseingang.findFirst({
      where: {
        rechnungsNummer: nummer,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByBestellung(bestellungId: string, tenantId: string): Promise<Rechnungseingang[]> {
    const results = await this.prisma.rechnungseingang.findMany({
      where: {
        bestellungId,
        tenantId,
        deletedAt: null
      },
      orderBy: { createdAt: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async findByWareneingang(wareneingangId: string, tenantId: string): Promise<Rechnungseingang[]> {
    const results = await this.prisma.rechnungseingang.findMany({
      where: {
        wareneingangId,
        tenantId,
        deletedAt: null
      },
      orderBy: { createdAt: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async findByTenant(tenantId: string, options?: {
    status?: RechnungseingangStatus
    lieferantId?: string
    bestellungId?: string
    wareneingangId?: string
    limit?: number
    offset?: number
  }): Promise<Rechnungseingang[]> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (options?.status) where.status = options.status
    if (options?.lieferantId) where.lieferantId = options.lieferantId
    if (options?.bestellungId) where.bestellungId = options.bestellungId
    if (options?.wareneingangId) where.wareneingangId = options.wareneingangId

    const results = await this.prisma.rechnungseingang.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findUeberfaellige(tenantId: string): Promise<Rechnungseingang[]> {
    // Vereinfachte Query - in Realität komplexer mit Zahlungsziel-Berechnung
    const results = await this.prisma.rechnungseingang.findMany({
      where: {
        tenantId,
        status: { in: [RechnungseingangStatus.VERBUCHT] },
        deletedAt: null,
        // Vereinfacht: Rechnungen älter als 30 Tage als überfällig
        rechnungsDatum: { lt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
      },
      orderBy: { rechnungsDatum: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async findMitAbweichungen(tenantId: string): Promise<Rechnungseingang[]> {
    const results = await this.prisma.rechnungseingang.findMany({
      where: {
        tenantId,
        deletedAt: null,
        abweichungen: { some: {} } as any // Hat Abweichungen
      } as any,
      orderBy: { createdAt: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async update(rechnung: Rechnungseingang): Promise<Rechnungseingang> {
    const data = {
      rechnungsNummer: rechnung.rechnungsNummer,
      lieferantId: rechnung.lieferantId,
      bestellungId: rechnung.bestellungId,
      wareneingangId: rechnung.wareneingangId,
      rechnungsDatum: rechnung.rechnungsDatum,
      status: rechnung.status,
      bruttoBetrag: rechnung.bruttoBetrag,
      nettoBetrag: rechnung.nettoBetrag,
      steuerBetrag: rechnung.steuerBetrag,
      steuerSatz: rechnung.steuerSatz,
      skonto: rechnung.skonto,
      zahlungsziel: rechnung.zahlungsziel,
      positionen: rechnung.positionen,
      abweichungen: rechnung.abweichungen,
      bemerkungen: rechnung.bemerkungen,
      version: rechnung.version,
      updatedAt: rechnung.updatedAt,
      deletedAt: rechnung.deletedAt
    }

    const updated = await this.prisma.rechnungseingang.update({
      where: { id: rechnung.id },
      data
    })

    return this.mapToEntity(updated)
  }

  async delete(id: string, tenantId: string): Promise<void> {
    await this.prisma.rechnungseingang.update({
      where: { id },
      data: { deletedAt: new Date() }
    })
  }

  async countByTenant(tenantId: string, status?: RechnungseingangStatus): Promise<number> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (status) where.status = status

    return this.prisma.rechnungseingang.count({ where })
  }

  async getGesamtOffen(tenantId: string): Promise<number> {
    const result = await this.prisma.rechnungseingang.aggregate({
      where: {
        tenantId,
        status: { in: [RechnungseingangStatus.VERBUCHT] },
        deletedAt: null
      },
      _sum: {
        bruttoBetrag: true
      }
    })

    return Number(result._sum.bruttoBetrag) || 0
  }

  private mapToEntity(data: any): Rechnungseingang {
    return new Rechnungseingang(
      data.id,
      data.rechnungsNummer,
      data.lieferantId,
      data.bestellungId,
      data.wareneingangId,
      data.rechnungsDatum,
      data.status,
      data.bruttoBetrag,
      data.nettoBetrag,
      data.steuerBetrag,
      data.steuerSatz,
      data.skonto,
      data.zahlungsziel,
      data.positionen,
      data.abweichungen,
      data.tenantId,
      data.bemerkungen,
      data.version,
      data.createdAt,
      data.updatedAt,
      data.deletedAt
    )
  }
}