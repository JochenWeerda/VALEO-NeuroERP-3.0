import { createReadStream } from 'fs'
import { parse } from 'csv-parse'
import { v4 as uuidv4 } from 'uuid'
import { db } from './db'
import { assertYear, normalizeName, parseAmount } from './utils'

export interface ImportOptions {
  year: number
  csvPath: string
  batchId?: string
  dataSource?: string
}

export async function runImport(opts: ImportOptions): Promise<void> {
  const { csvPath } = opts
  const year = Number(opts.year)
  assertYear(year)
  const batchId = opts.batchId ?? uuidv4()
  const dataSource = opts.dataSource ?? `agrarzahlungen_de_${year}`

  console.log(`Importing GAP CSV for year ${year} from ${csvPath} (batch ${batchId})`)

  const parser = createReadStream(csvPath).pipe(
    parse({
      delimiter: ';',
      columns: true,
      bom: true,
      relaxColumnCount: true,
      skipEmptyLines: true,
      trim: true,
      relaxQuotes: true,
      escape: '"',
      quote: '"',
      skipRecordsWithError: true,
      on_record: (record, context) => {
        // Skip records with parsing errors
        return record
      },
    }),
  )

  let rowCount = 0

  for await (const row of parser) {
    const beneficiaryNameRaw = 
      row['Name des Begünstigten/Rechtsträgers/Verdands'] ?? 
      row['Name'] ?? 
      row['Beguenstigter'] ?? 
      ''
    if (!beneficiaryNameRaw) {
      continue
    }

    const beneficiaryNameNorm = normalizeName(beneficiaryNameRaw)
    const postalCode = row['PLZ'] ?? row['Postleitzahl'] ?? null
    const city = row['Gemeinde'] ?? row['Ort'] ?? row['Ort/Stadt'] ?? null
    const regionCode = row['RegionCode'] ?? row['Bundesland Code'] ?? null
    const regionName = row['RegionName'] ?? row['Bundesland'] ?? null
    const streetRaw = row['Strasse'] ?? row['Straße'] ?? null
    const measureCode = 
      row['Code der Maßnahme/der Interventionskategorie/des Sektors gemäß Anhang IX '] ?? 
      row['Code der Maßnahme/der Interventionskategorie/des Sektors gemäß Anhang IX'] ??
      row['Maßnahmencode'] ?? 
      row['Massnahme'] ?? 
      null
    const measureDescription = row['Maßnahme'] ?? row['Massnahme Text'] ?? null
    const amountTotal = parseAmount(
      row['EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten*'] ??
      row['EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten'] ??
      row['Betrag (gesamt)'] ?? 
      row['EU-Betrag (EGFL und ELER) ...']
    )
    const amountEgfl = parseAmount(
      row['EGFL- Gesamtbetrag für diesen Begünstigten'] ??
      row['EGFL- Gesamtbetrag für diesen Begünstigten'] ??
      row['EGFL'] ?? 
      row['EGFL-Betrag']
    )
    const amountEler = parseAmount(
      row['ELER-Gesamtbetrag für diesen Begünstigten (EU-Mittel)'] ??
      row['ELER'] ?? 
      row['ELER-Betrag']
    )
    const amountNational = parseAmount(
      row['National kofinanzierter Gesamtbetrag für diesen Begünstigten'] ??
      row['Nationale Kofinanzierung']
    )

    await db.query(
      `
      INSERT INTO gap_payments (
        ref_year,
        data_source,
        member_state,
        region_code,
        region_name,
        beneficiary_name_raw,
        beneficiary_name_norm,
        street_raw,
        postal_code,
        city,
        measure_code,
        measure_description,
        amount_egfl,
        amount_eler,
        amount_national_cofin,
        amount_total,
        load_batch_id,
        raw_row
      ) VALUES (
        $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,
        $11,$12,$13,$14,$15,$16,$17,$18
      )
      `,
      [
        year,
        dataSource,
        (row['EU-Mitglied'] ?? 'DE').toString().slice(0, 2).toUpperCase(),
        regionCode,
        regionName,
        beneficiaryNameRaw,
        beneficiaryNameNorm,
        streetRaw,
        postalCode,
        city,
        measureCode,
        measureDescription,
        amountEgfl,
        amountEler,
        amountNational,
        amountTotal,
        batchId,
        row,
      ],
    )

    rowCount += 1
    if (rowCount % 1000 === 0) {
      console.log(`  inserted ${rowCount} rows...`)
    }
  }

  console.log(`Import completed for year ${year}, batch ${batchId}. Rows inserted: ${rowCount}`)
}
