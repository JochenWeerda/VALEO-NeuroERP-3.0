/**
 * Webhook ID Value Object
 */

import { z } from 'zod';
import { generatePrefixedId, isValidId } from '@shared/utils/id-generator.js';

const WebhookIdSchema = z.string().uuid();

export class WebhookId {
  private readonly _value: string;

  private constructor(value: string) {
    if (!isValidId(value)) {
      throw new Error(`Invalid WebhookId: ${value}`);
    }
    this._value = value;
  }

  static create(): WebhookId {
    return new WebhookId(generatePrefixedId('wh'));
  }

  static fromString(value: string): WebhookId {
    WebhookIdSchema.parse(value);
    return new WebhookId(value);
  }

  get value(): string {
    return this._value;
  }

  equals(other: WebhookId): boolean {
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }

  toJSON(): string {
    return this._value;
  }
}
