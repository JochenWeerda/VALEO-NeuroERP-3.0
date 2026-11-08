CREATE TABLE "channel_configs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"channel" text NOT NULL,
	"provider" text NOT NULL,
	"credentials" jsonb NOT NULL,
	"rate_limit" jsonb,
	"retry_policy" jsonb,
	"active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "delivery_receipts" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"message_id" uuid NOT NULL,
	"channel" text NOT NULL,
	"provider" text NOT NULL,
	"status" text NOT NULL,
	"meta" jsonb,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "notification_messages" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"channel" text NOT NULL,
	"template_key" text,
	"locale" text DEFAULT 'de-DE' NOT NULL,
	"payload" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"recipients" jsonb NOT NULL,
	"attachments" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"priority" text DEFAULT 'Normal' NOT NULL,
	"status" text DEFAULT 'Pending' NOT NULL,
	"attempt_count" integer DEFAULT 0 NOT NULL,
	"last_error" text,
	"sent_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "notification_templates" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"key" text NOT NULL,
	"name" text NOT NULL,
	"channel" text NOT NULL,
	"locale" text DEFAULT 'de-DE' NOT NULL,
	"subject" text,
	"body_text" text NOT NULL,
	"body_html" text,
	"placeholders" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"status" text DEFAULT 'Draft' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE INDEX "cfg_tenant_idx" ON "channel_configs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "cfg_channel_idx" ON "channel_configs" USING btree ("channel");--> statement-breakpoint
CREATE INDEX "rcpt_message_idx" ON "delivery_receipts" USING btree ("message_id");--> statement-breakpoint
CREATE INDEX "rcpt_status_idx" ON "delivery_receipts" USING btree ("status");--> statement-breakpoint
CREATE INDEX "nmsg_tenant_idx" ON "notification_messages" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "nmsg_status_idx" ON "notification_messages" USING btree ("status");--> statement-breakpoint
CREATE INDEX "nmsg_channel_idx" ON "notification_messages" USING btree ("channel");--> statement-breakpoint
CREATE INDEX "nmsg_created_at_idx" ON "notification_messages" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "ntpl_tenant_idx" ON "notification_templates" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "ntpl_key_idx" ON "notification_templates" USING btree ("key");--> statement-breakpoint
CREATE INDEX "ntpl_channel_idx" ON "notification_templates" USING btree ("channel");