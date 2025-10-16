import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { Anfrage } from '../../core/entities/anfrage.entity'
import { AnfrageRepository } from '../../core/repositories/anfrage.repository'
import { AnfrageStatus, Prioritaet } from '../../core/entities/anfrage.entity'

@injectable()
export class AnfragePostgresRepository implements AnfrageRepository {
  constructor(private prisma: PrismaClient) {}

  async save(anfrage: Anfrage): Promise<Anfrage> {
    const data = {
      id: anfrage.id,
      anfrageNummer: anfrage.anfrageNummer,
      typ: anfrage.typ,
      anforderer: anfrage.anforderer,
      artikel: anfrage.artikel,
      menge: anfrage.menge,
      einheit: anfrage.einheit,
      prioritaet: anfrage.prioritaet,
      faelligkeit: anfrage.faelligkeit,
      status: anfrage.status,
      begruendung: anfrage.begruendung,
      kostenstelle: anfrage.kostenstelle,
      projekt: anfrage.projekt,
      bemerkungen: anfrage.bemerkungen,
      tenantId: anfrage.tenantId,
      version: anfrage.version,
      createdAt: anfrage.createdAt,
      updatedAt: anfrage.updatedAt,
      deletedAt: anfrage.deletedAt
    }

    const saved = await this.prisma.anfrage.upsert({
      where: { id: anfrage.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<Anfrage | null> {
    const result = await this.prisma.anfrage.findFirst({
      where: {
        id,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByNummer(nummer: string, tenantId: string): Promise<Anfrage | null> {
    const result = await this.prisma.anfrage.findFirst({
      where: {
        anfrageNummer: nummer,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByTenant(tenantId: string, options?: {
    status?: AnfrageStatus
    prioritaet?: Prioritaet
    anforderer?: string
    limit?: number
    offset?: number
  }): Promise<Anfrage[]> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (options?.status) where.status = options.status
    if (options?.prioritaet) where.prioritaet = options.prioritaet
    if (options?.anforderer) where.anforderer = options.anforderer

    const results = await this.prisma.anfrage.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findUeberfaellige(tenantId: string): Promise<Anfrage[]> {
    const results = await this.prisma.anfrage.findMany({
      where: {
        tenantId,
        faelligkeit: { lt: new Date() },
        status: { not: AnfrageStatus.ENTWURF },
        deletedAt: null
      },
      orderBy: { faelligkeit: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async findDringende(tenantId: string): Promise<Anfrage[]> {
    const results = await this.prisma.anfrage.findMany({
      where: {
        tenantId,
        prioritaet: Prioritaet.DRINGEND,
        status: { not: AnfrageStatus.ENTWURF },
        deletedAt: null
      },
      orderBy: { faelligkeit: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async update(anfrage: Anfrage): Promise<Anfrage> {
    const data = {
      anfrageNummer: anfrage.anfrageNummer,
      typ: anfrage.typ,
      anforderer: anfrage.anforderer,
      artikel: anfrage.artikel,
      menge: anfrage.menge,
      einheit: anfrage.einheit,
      prioritaet: anfrage.prioritaet,
      faelligkeit: anfrage.faelligkeit,
      status: anfrage.status,
      begruendung: anfrage.begruendung,
      kostenstelle: anfrage.kostenstelle,
      projekt: anfrage.projekt,
      bemerkungen: anfrage.bemerkungen,
      version: anfrage.version,
      updatedAt: anfrage.updatedAt,
      deletedAt: anfrage.deletedAt
    }

    const updated = await this.prisma.anfrage.update({
      where: { id: anfrage.id },
      data
    })

    return this.mapToEntity(updated)
  }

  async delete(id: string, tenantId: string): Promise<void> {
    await this.prisma.anfrage.update({
      where: { id },
      data: { deletedAt: new Date() }
    })
  }

  async countByTenant(tenantId: string, status?: AnfrageStatus): Promise<number> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (status) where.status = status

    return this.prisma.anfrage.count({ where })
  }

  private mapToEntity(data: any): Anfrage {
    return new Anfrage(
      data.id,
      data.anfrageNummer,
      data.typ,
      data.anforderer,
      data.artikel,
      data.menge,
      data.einheit,
      data.prioritaet,
      data.faelligkeit,
      data.status,
      data.begruendung,
      data.tenantId,
      data.kostenstelle,
      data.projekt,
      data.bemerkungen,
      data.version,
      data.createdAt,
      data.updatedAt,
      data.deletedAt
    )
  }
}