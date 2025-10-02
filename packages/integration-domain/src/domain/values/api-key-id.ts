/**
 * API Key ID Value Object
 */

import { z } from 'zod';
import { generatePrefixedId, isValidId } from '@shared/utils/id-generator.js';

const ApiKeyIdSchema = z.string().uuid();

export class ApiKeyId {
  private readonly _value: string;

  private constructor(value: string) {
    if (!isValidId(value)) {
      throw new Error(`Invalid ApiKeyId: ${value}`);
    }
    this._value = value;
  }

  static create(): ApiKeyId {
    return new ApiKeyId(generatePrefixedId('ak'));
  }

  static fromString(value: string): ApiKeyId {
    ApiKeyIdSchema.parse(value);
    return new ApiKeyId(value);
  }

  get value(): string {
    return this._value;
  }

  equals(other: ApiKeyId): boolean {
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }

  toJSON(): string {
    return this._value;
  }
}
