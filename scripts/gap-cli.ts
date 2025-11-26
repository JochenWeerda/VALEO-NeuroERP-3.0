#!/usr/bin/env ts-node
import { Command } from 'commander'
import { runImport } from './gap/import'
import { runAggregate } from './gap/aggregate'
import { runMatch } from './gap/match'
import { runSnapshot } from './gap/snapshot'
import { runHydrateCustomers } from './gap/hydrate-customers'

const program = new Command()

program.name('gap-cli').description('GAP ETL & Potential Pipeline').version('1.0.0')

program
  .command('import')
  .description('Import GAP CSV for a given year into gap_payments')
  .requiredOption('--year <number>', 'reference year', (v) => parseInt(v, 10))
  .requiredOption('--csv-path <path>', 'path to impdata CSV')
  .option('--batch-id <uuid>', 'custom load batch id')
  .action(async (opts) => {
    await runImport({ year: opts.year, csvPath: opts.csvPath, batchId: opts.batchId })
  })

program
  .command('aggregate')
  .description('Aggregate direct payments per beneficiary for a given year')
  .requiredOption('--year <number>', 'reference year', (v) => parseInt(v, 10))
  .action(runAggregate)

program
  .command('match')
  .description('Match customers to GAP beneficiaries for a given year')
  .requiredOption('--year <number>', 'reference year', (v) => parseInt(v, 10))
  .action(runMatch)

program
  .command('snapshot')
  .description('Compute customer_potential_snapshot for a given year')
  .requiredOption('--year <number>', 'reference year', (v) => parseInt(v, 10))
  .option('--eur-per-ha <number>', 'override EUR/ha conversion', (v) => parseFloat(v))
  .action((opts) => runSnapshot({ year: opts.year, eurPerHa: opts.eurPerHa }))

program
  .command('hydrate-customers')
  .description('Update customer analytics fields from snapshot for a given year')
  .requiredOption('--year <number>', 'reference year', (v) => parseInt(v, 10))
  .action(runHydrateCustomers)

program
  .command('run-year')
  .description('Run full GAP pipeline for a given year (import -> aggregate -> match -> snapshot -> hydrate)')
  .requiredOption('--year <number>', 'reference year', (v) => parseInt(v, 10))
  .requiredOption('--csv-path <path>', 'path to impdata CSV')
  .option('--batch-id <uuid>', 'custom load batch id for import')
  .action(async (opts) => {
    const { year, csvPath, batchId } = opts
    await runImport({ year, csvPath, batchId })
    await runAggregate({ year })
    await runMatch({ year })
    await runSnapshot({ year })
    await runHydrateCustomers({ year })
  })

program.parseAsync(process.argv).catch((err) => {
  console.error(err)
  process.exit(1)
})
