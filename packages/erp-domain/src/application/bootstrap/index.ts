import { Router } from 'express';
import { getErpPool } from '../../infrastructure/persistence/postgres';
import { initFinanzKontoModule } from './finanzKonto.bootstrap';
import { initFinanzBuchungModule } from './finanzBuchung.bootstrap';
import { initFinanzDebitorModule } from './finanzDebitor.bootstrap';
import { initFinanzKreditorModule } from './finanzKreditor.bootstrap';
import { initFinanzBankkontoModule } from './finanzBankkonto.bootstrap';

export interface FinanceModuleOptions {
  reusePool?: boolean;
}

export function buildFinanceRouter(options: FinanceModuleOptions = {}): Router {
  const pool = getErpPool();
  const financeRouter = Router();

  const konto = initFinanzKontoModule({ pool });
  financeRouter.use(konto.router);

  const buchung = initFinanzBuchungModule({ pool });
  financeRouter.use(buchung.router);

  const debitor = initFinanzDebitorModule({ pool });
  financeRouter.use(debitor.router);

  const kreditor = initFinanzKreditorModule({ pool });
  financeRouter.use(kreditor.router);

  const bankkonto = initFinanzBankkontoModule({ pool });
  financeRouter.use(bankkonto.router);

  return financeRouter;
}