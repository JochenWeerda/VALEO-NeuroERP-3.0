import { type ContractRecord, contracts } from './data';

export async function listContracts(status?: ContractRecord['status']): Promise<ContractRecord[]> {
  if (status === undefined) {
    return contracts;
  }

  return contracts.filter((contract) => contract.status === status);
}
