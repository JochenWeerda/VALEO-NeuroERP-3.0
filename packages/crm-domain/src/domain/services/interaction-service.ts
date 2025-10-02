import { v4 as uuidv4 } from 'uuid';
import { InteractionEntity, CreateInteractionInput, UpdateInteractionInput, InteractionTypeType } from '../entities';
import { InteractionRepository } from '../../infra/repo';

export interface InteractionServiceDependencies {
  interactionRepo: InteractionRepository;
}

export interface CreateInteractionData extends CreateInteractionInput {
  tenantId: string;
  occurredAt: Date;
}

export interface UpdateInteractionData extends UpdateInteractionInput {
  tenantId: string;
  occurredAt?: Date;
}

export class InteractionService {
  constructor(private deps: InteractionServiceDependencies) {}

  async createInteraction(data: CreateInteractionData): Promise<InteractionEntity> {
    // Business validation
    if (data.occurredAt > new Date()) {
      throw new Error('Interaction cannot be scheduled for the future');
    }

    const interaction = await this.deps.interactionRepo.create(data);
    return interaction;
  }

  async getInteraction(id: string, tenantId: string): Promise<InteractionEntity | null> {
    return this.deps.interactionRepo.findById(id, tenantId);
  }

  async getInteractionsByCustomer(
    customerId: string,
    tenantId: string,
    filters: {
      type?: InteractionTypeType;
      from?: Date;
      to?: Date;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.interactionRepo.findByCustomerId(customerId, tenantId, filters, pagination);
  }

  async updateInteraction(id: string, data: UpdateInteractionData): Promise<InteractionEntity> {
    const existingInteraction = await this.deps.interactionRepo.findById(id, data.tenantId);
    if (!existingInteraction) {
      throw new Error(`Interaction ${id} not found`);
    }

    // Business validation
    if (data.occurredAt && data.occurredAt > new Date()) {
      throw new Error('Interaction cannot be scheduled for the future');
    }

    const updatedInteraction = await this.deps.interactionRepo.update(id, data.tenantId, data);

    if (!updatedInteraction) {
      throw new Error(`Failed to update interaction ${id}`);
    }

    return updatedInteraction;
  }

  async deleteInteraction(id: string, tenantId: string): Promise<boolean> {
    const interaction = await this.deps.interactionRepo.findById(id, tenantId);
    if (!interaction) {
      throw new Error(`Interaction ${id} not found`);
    }

    return this.deps.interactionRepo.delete(id, tenantId);
  }

  async getUpcomingInteractions(tenantId: string, from?: Date): Promise<InteractionEntity[]> {
    return this.deps.interactionRepo.getUpcomingInteractions(tenantId, from);
  }

  async getOverdueInteractions(tenantId: string): Promise<InteractionEntity[]> {
    return this.deps.interactionRepo.getOverdueInteractions(tenantId);
  }

  async getTodaysInteractions(tenantId: string): Promise<InteractionEntity[]> {
    return this.deps.interactionRepo.getTodaysInteractions(tenantId);
  }

  async getInteractionsByType(type: InteractionTypeType, tenantId: string): Promise<InteractionEntity[]> {
    return this.deps.interactionRepo.getByType(type, tenantId);
  }

  async addAttachment(
    interactionId: string,
    tenantId: string,
    attachment: {
      filename: string;
      url: string;
      size: number;
      mimeType: string;
    }
  ): Promise<InteractionEntity> {
    const interaction = await this.deps.interactionRepo.findById(interactionId, tenantId);
    if (!interaction) {
      throw new Error(`Interaction ${interactionId} not found`);
    }

    // Create attachment with ID
    const newAttachment = {
      id: uuidv4(),
      ...attachment
    };

    // Update interaction with new attachment
    const updatedInteraction = await this.deps.interactionRepo.update(
      interactionId,
      tenantId,
      {
        attachments: [...interaction.attachments, newAttachment]
      }
    );

    if (!updatedInteraction) {
      throw new Error(`Failed to add attachment to interaction`);
    }

    return updatedInteraction;
  }

  async removeAttachment(interactionId: string, tenantId: string, attachmentId: string): Promise<InteractionEntity> {
    const interaction = await this.deps.interactionRepo.findById(interactionId, tenantId);
    if (!interaction) {
      throw new Error(`Interaction ${interactionId} not found`);
    }

    const attachmentExists = interaction.attachments.some(att => att.id === attachmentId);
    if (!attachmentExists) {
      throw new Error(`Attachment ${attachmentId} not found`);
    }

    const updatedAttachments = interaction.attachments.filter(att => att.id !== attachmentId);

    const updatedInteraction = await this.deps.interactionRepo.update(
      interactionId,
      tenantId,
      { attachments: updatedAttachments }
    );

    if (!updatedInteraction) {
      throw new Error(`Failed to remove attachment from interaction`);
    }

    return updatedInteraction;
  }
}