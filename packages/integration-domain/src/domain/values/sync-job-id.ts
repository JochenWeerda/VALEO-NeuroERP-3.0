/**
 * Sync Job ID Value Object
 */

import { z } from 'zod';
import { generatePrefixedId, isValidId } from '@shared/utils/id-generator.js';

const SyncJobIdSchema = z.string().uuid();

export class SyncJobId {
  private readonly _value: string;

  private constructor(value: string) {
    if (!isValidId(value)) {
      throw new Error(`Invalid SyncJobId: ${value}`);
    }
    this._value = value;
  }

  static create(): SyncJobId {
    return new SyncJobId(generatePrefixedId('sj'));
  }

  static fromString(value: string): SyncJobId {
    SyncJobIdSchema.parse(value);
    return new SyncJobId(value);
  }

  get value(): string {
    return this._value;
  }

  equals(other: SyncJobId): boolean {
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }

  toJSON(): string {
    return this._value;
  }
}
