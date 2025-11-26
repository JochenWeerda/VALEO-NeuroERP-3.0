#!/usr/bin/env ts-node
import { readFileSync } from 'fs'
import { resolve } from 'path'
import { db } from './db'

async function runMigration(sqlFile: string, description: string): Promise<void> {
  console.log(`\n${description}...`)
  const sqlPath = resolve(__dirname, '../../database', sqlFile)
  const sql = readFileSync(sqlPath, 'utf8')
  
  try {
    await db.query(sql)
    console.log(`✅ ${description} erfolgreich ausgeführt`)
  } catch (error: any) {
    if (error.message?.includes('already exists') || error.message?.includes('duplicate')) {
      console.log(`⚠️  ${description} - Spalten existieren bereits (OK)`)
    } else {
      console.error(`❌ Fehler bei ${description}:`, error.message)
      throw error
    }
  }
}

async function main() {
  const databaseUrl = process.env.DATABASE_URL
  if (!databaseUrl) {
    console.error('❌ DATABASE_URL nicht gesetzt!')
    console.log('Setze: $env:DATABASE_URL="postgresql://user:pass@host:port/dbname"')
    process.exit(1)
  }

  console.log('🚀 Starte SQL-Migrationen für Prospecting-Workflow...')
  console.log(`📊 Datenbank: ${databaseUrl.replace(/:[^:@]+@/, ':****@')}`)

  try {
    await runMigration('analytics-customer-fields.sql', 'Analytics-Felder im Customer-Table')
    await runMigration('analytics-gap.sql', 'GAP-Basis-Tabellen')
    
    console.log('\n✅ Alle Migrationen erfolgreich abgeschlossen!')
  } catch (error) {
    console.error('\n❌ Migrationen fehlgeschlagen:', error)
    process.exit(1)
  } finally {
    await db.end()
  }
}

main().catch(console.error)

