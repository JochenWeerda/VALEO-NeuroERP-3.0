"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CalendarEntity = void 0;
const uuid_1 = require("uuid");
class CalendarEntity {
    id;
    tenantId;
    key;
    name;
    holidays;
    businessDays;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id || (0, uuid_1.v4)();
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
    validate() {
        if (!this.key) {
            throw new Error('key is required');
        }
        if (!this.name) {
            throw new Error('name is required');
        }
        const validDays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
        for (const day of Object.keys(this.businessDays)) {
            if (!validDays.includes(day)) {
                throw new Error(`Invalid business day: ${day}`);
            }
        }
    }
    isHoliday(date) {
        const dateStr = date.toISOString().split('T')[0];
        return this.holidays.some(holiday => {
            const holidayStr = holiday.toISOString().split('T')[0];
            return holidayStr === dateStr;
        });
    }
    isBusinessDay(date) {
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' }).toLowerCase();
        return this.businessDays[dayName] === true;
    }
    isWorkingDay(date) {
        return this.isBusinessDay(date) && !this.isHoliday(date);
    }
    getNextWorkingDay(fromDate) {
        let date = new Date(fromDate);
        date.setDate(date.getDate() + 1);
        while (!this.isWorkingDay(date)) {
            date.setDate(date.getDate() + 1);
        }
        return date;
    }
    getPreviousWorkingDay(fromDate) {
        let date = new Date(fromDate);
        date.setDate(date.getDate() - 1);
        while (!this.isWorkingDay(date)) {
            date.setDate(date.getDate() - 1);
        }
        return date;
    }
    addWorkingDays(date, days) {
        if (days === 0)
            return new Date(date);
        let result = new Date(date);
        let remaining = Math.abs(days);
        let direction = days > 0 ? 1 : -1;
        while (remaining > 0) {
            result.setDate(result.getDate() + direction);
            if (this.isWorkingDay(result)) {
                remaining--;
            }
        }
        return result;
    }
    getWorkingDaysInRange(startDate, endDate) {
        const workingDays = [];
        let current = new Date(startDate);
        while (current <= endDate) {
            if (this.isWorkingDay(current)) {
                workingDays.push(new Date(current));
            }
            current.setDate(current.getDate() + 1);
        }
        return workingDays;
    }
    updateHolidays(holidays) {
        return new CalendarEntity({
            ...this,
            holidays,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    updateBusinessDays(businessDays) {
        return new CalendarEntity({
            ...this,
            businessDays: { ...this.businessDays, ...businessDays },
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    static createGermanCalendar(tenantId) {
        const germanHolidays = [
            new Date('2025-01-01'),
            new Date('2025-04-18'),
            new Date('2025-04-21'),
            new Date('2025-05-01'),
            new Date('2025-05-29'),
            new Date('2025-06-09'),
            new Date('2025-10-03'),
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
exports.CalendarEntity = CalendarEntity;
//# sourceMappingURL=calendar.js.map