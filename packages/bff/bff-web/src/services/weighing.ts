import { type WeighingTicket, weighingTickets } from './data';

export async function listWeighingTickets(): Promise<WeighingTicket[]> {
  return weighingTickets;
}

export async function updateWeighingTicket(updated: WeighingTicket): Promise<WeighingTicket> {
  const index = weighingTickets.findIndex((ticket) => ticket.id === updated.id);
  if (index === -1) {
    throw new Error(`Ticket ${updated.id} not found`);
  }

  weighingTickets[index] = { ...updated };
  return weighingTickets[index];
}

export async function finalizeWeighingTicket(id: string): Promise<WeighingTicket> {
  const ticket = weighingTickets.find((item) => item.id === id);
  if (ticket === undefined) {
    throw new Error(`Ticket ${id} not found`);
  }

  ticket.status = 'completed';
  ticket.ts = new Date().toISOString();
  return ticket;
}
