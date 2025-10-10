import { v4 as uuidv4 } from 'uuid';

export class CalendarEntity {
  public readonly id: string;
  public readonly tenantId?: string; // null for global calendars
  public readonly key: string; // e.g., "DE-BY-AGRI"
  public readonly name: string;
  public readonly holidays: Date[]; // Holiday dates
  public readonly businessDays: Record<string, boolean>; // mon, tue, wed, thu, fri, sat, sun
  public readonly createdAt: Date;
  public readonly updatedAt: Date;
  public readonly version: number;

  constructor(props: {
    id?: string;
    tenantId?: string;
    key: string;
    name: string;
    holidays?: Date[];
    businessDays?: Record<string, boolean>;
    createdAt?: Date;
    updatedAt?: Date;
    version?: number;
  }) {
    this.id = props.id || uuidv4();
    this.tenantId = props.tenantId;
    this.key = props.key;
    this.name = props.name;
    this.holidays = props.holidays || [];
    this.businessDays = {
      mon: true,
      tue: true,
      wed: true,
      thu: true,
      fri: true,
      sat: false,
      sun: false,
      ...props.businessDays,
    };
    this.createdAt = props.createdAt || new Date();
    this.updatedAt = props.updatedAt || new Date();
    this.version = props.version || 1;

    this.validate();
  }

  private validate(): void {
    if (!this.key) {
      throw new Error('key is required');
    }
    if (!this.name) {
      throw new Error('name is required');
    }

    // Validate business days keys
    const validDays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
    for (const day of Object.keys(this.businessDays)) {
      if (!validDays.includes(day)) {
        throw new Error(`Invalid business day: ${day}`);
      }
    }
  }

  public isHoliday(date: Date): boolean {
    const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD format
    return this.holidays.some(holiday => {
      const holidayStr = holiday.toISOString().split('T')[0];
      return holidayStr === dateStr;
    });
  }

  public isBusinessDay(date: Date): boolean {
    const dayName = date.toLocaleDateString('en-US', { weekday: 'short' }).toLowerCase();
    return this.businessDays[dayName] === true;
  }

  public isWorkingDay(date: Date): boolean {
    return this.isBusinessDay(date) && !this.isHoliday(date);
  }

  public getNextWorkingDay(fromDate: Date): Date {
    const date = new Date(fromDate);

    // Start from the next day
    date.setDate(date.getDate() + 1);

    // Find the next working day
    while (!this.isWorkingDay(date)) {
      date.setDate(date.getDate() + 1);
    }

    return date;
  }

  public getPreviousWorkingDay(fromDate: Date): Date {
    const date = new Date(fromDate);

    // Start from the previous day
    date.setDate(date.getDate() - 1);

    // Find the previous working day
    while (!this.isWorkingDay(date)) {
      date.setDate(date.getDate() - 1);
    }

    return date;
  }

  public addWorkingDays(date: Date, days: number): Date {
    if (days === 0) return new Date(date);

    const result = new Date(date);
    let remaining = Math.abs(days);
    const direction = days > 0 ? 1 : -1;

    while (remaining > 0) {
      result.setDate(result.getDate() + direction);
      if (this.isWorkingDay(result)) {
        remaining--;
      }
    }

    return result;
  }

  public getWorkingDaysInRange(startDate: Date, endDate: Date): Date[] {
    const workingDays: Date[] = [];
    const current = new Date(startDate);

    while (current <= endDate) {
      if (this.isWorkingDay(current)) {
        workingDays.push(new Date(current));
      }
      current.setDate(current.getDate() + 1);
    }

    return workingDays;
  }

  public updateHolidays(holidays: Date[]): CalendarEntity {
    return new CalendarEntity({
      ...this,
      holidays,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public updateBusinessDays(businessDays: Record<string, boolean>): CalendarEntity {
    return new CalendarEntity({
      ...this,
      businessDays: { ...this.businessDays, ...businessDays },
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public static createGermanCalendar(tenantId?: string): CalendarEntity {
    // German federal holidays (simplified - would need to be more comprehensive)
    const germanHolidays = [
      // New Year's Day
      new Date('2025-01-01'),
      // Good Friday (varies)
      new Date('2025-04-18'),
      // Easter Monday (varies)
      new Date('2025-04-21'),
      // Labor Day
      new Date('2025-05-01'),
      // Ascension Day (varies)
      new Date('2025-05-29'),
      // Whit Monday (varies)
      new Date('2025-06-09'),
      // German Unity Day
      new Date('2025-10-03'),
      // Christmas
      new Date('2025-12-25'),
      new Date('2025-12-26'),
    ];

    return new CalendarEntity({
      tenantId,
      key: 'DE',
      name: 'German Federal Holidays',
      holidays: germanHolidays,
      businessDays: {
        mon: true,
        tue: true,
        wed: true,
        thu: true,
        fri: true,
        sat: false,
        sun: false,
      },
    });
  }
}