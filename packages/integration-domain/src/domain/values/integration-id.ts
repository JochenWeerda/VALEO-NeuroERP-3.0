/**
 * Integration ID Value Object
 */

import { z } from 'zod';
import { generatePrefixedId, isValidId } from '@shared/utils/id-generator.js';

const IntegrationIdSchema = z.string().uuid();

export class IntegrationId {
  private readonly _value: string;

  private constructor(value: string) {
    if (!isValidId(value)) {
      throw new Error(`Invalid IntegrationId: ${value}`);
    }
    this._value = value;
  }

  static create(): IntegrationId {
    return new IntegrationId(generatePrefixedId('int'));
  }

  static fromString(value: string): IntegrationId {
    IntegrationIdSchema.parse(value);
    return new IntegrationId(value);
  }

  get value(): string {
    return this._value;
  }

  equals(other: IntegrationId): boolean {
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }

  toJSON(): string {
    return this._value;
  }
}
