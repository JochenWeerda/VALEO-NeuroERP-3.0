"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InteractionEntity = exports.AttachmentSchema = exports.UpdateInteractionInputSchema = exports.CreateInteractionInputSchema = exports.InteractionSchema = exports.InteractionType = void 0;
const zod_1 = require("zod");
const uuid_1 = require("uuid");
// Enums
exports.InteractionType = {
    CALL: 'Call',
    EMAIL: 'Email',
    VISIT: 'Visit',
    NOTE: 'Note'
};
// Interaction Entity Schema
exports.InteractionSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    customerId: zod_1.z.string().uuid(),
    contactId: zod_1.z.string().uuid().optional(),
    type: zod_1.z.enum([
        exports.InteractionType.CALL,
        exports.InteractionType.EMAIL,
        exports.InteractionType.VISIT,
        exports.InteractionType.NOTE
    ]),
    subject: zod_1.z.string().min(1),
    content: zod_1.z.string().min(1),
    occurredAt: zod_1.z.date(),
    createdBy: zod_1.z.string().uuid(),
    attachments: zod_1.z.array(zod_1.z.object({
        id: zod_1.z.string().uuid(),
        filename: zod_1.z.string(),
        url: zod_1.z.string().url(),
        size: zod_1.z.number().nonnegative(),
        mimeType: zod_1.z.string()
    })).default([]),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    version: zod_1.z.number().int().nonnegative()
});
// Create Interaction Input Schema (for API)
exports.CreateInteractionInputSchema = exports.InteractionSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    version: true
});
// Update Interaction Input Schema (for API)
exports.UpdateInteractionInputSchema = zod_1.z.object({
    subject: zod_1.z.string().min(1).optional(),
    content: zod_1.z.string().min(1).optional(),
    occurredAt: zod_1.z.date().optional(),
    attachments: zod_1.z.array(zod_1.z.object({
        id: zod_1.z.string().uuid(),
        filename: zod_1.z.string(),
        url: zod_1.z.string().url(),
        size: zod_1.z.number().nonnegative(),
        mimeType: zod_1.z.string()
    })).optional()
});
// Attachment Schema for API responses
exports.AttachmentSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    filename: zod_1.z.string(),
    url: zod_1.z.string().url(),
    size: zod_1.z.number().nonnegative(),
    mimeType: zod_1.z.string()
});
// Interaction Aggregate Root
class InteractionEntity {
    props;
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        const now = new Date();
        const interaction = {
            ...props,
            id: (0, uuid_1.v4)(),
            attachments: props.attachments || [],
            createdAt: now,
            updatedAt: now,
            version: 1
        };
        return new InteractionEntity(interaction);
    }
    static fromPersistence(props) {
        return new InteractionEntity({
            ...props,
            contactId: props.contactId ?? undefined,
        });
    }
    update(props) {
        if (props.subject !== undefined) {
            this.props.subject = props.subject;
        }
        if (props.content !== undefined) {
            this.props.content = props.content;
        }
        if (props.occurredAt !== undefined) {
            this.props.occurredAt = props.occurredAt;
        }
        if (props.attachments !== undefined) {
            this.props.attachments = props.attachments;
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    addAttachment(attachment) {
        const newAttachment = {
            ...attachment,
            id: (0, uuid_1.v4)()
        };
        this.props.attachments.push(newAttachment);
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    removeAttachment(attachmentId) {
        const index = this.props.attachments.findIndex(att => att.id === attachmentId);
        if (index > -1) {
            this.props.attachments.splice(index, 1);
            this.props.updatedAt = new Date();
            this.props.version += 1;
        }
    }
    updateContent(subject, content) {
        this.props.subject = subject;
        this.props.content = content;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    reschedule(occurredAt) {
        this.props.occurredAt = occurredAt;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    // Business logic methods
    isOverdue() {
        return this.props.occurredAt < new Date();
    }
    isToday() {
        const today = new Date();
        const interactionDate = new Date(this.props.occurredAt);
        return (today.getDate() === interactionDate.getDate() &&
            today.getMonth() === interactionDate.getMonth() &&
            today.getFullYear() === interactionDate.getFullYear());
    }
    isUpcoming() {
        return this.props.occurredAt > new Date();
    }
    // Getters
    get id() { return this.props.id; }
    get tenantId() { return this.props.tenantId; }
    get customerId() { return this.props.customerId; }
    get contactId() { return this.props.contactId; }
    get type() { return this.props.type; }
    get subject() { return this.props.subject; }
    get content() { return this.props.content; }
    get occurredAt() { return this.props.occurredAt; }
    get createdBy() { return this.props.createdBy; }
    get attachments() { return [...this.props.attachments]; }
    get createdAt() { return this.props.createdAt; }
    get updatedAt() { return this.props.updatedAt; }
    get version() { return this.props.version; }
    // Export for persistence
    toPersistence() {
        return { ...this.props };
    }
    // Export for API responses
    toJSON() {
        const { tenantId, ...interactionWithoutTenant } = this.props;
        return interactionWithoutTenant;
    }
}
exports.InteractionEntity = InteractionEntity;
//# sourceMappingURL=interaction.js.map