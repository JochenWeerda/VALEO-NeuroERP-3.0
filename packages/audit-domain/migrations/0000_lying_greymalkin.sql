CREATE TABLE "audit_events" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"timestamp" timestamp with time zone NOT NULL,
	"actor" jsonb NOT NULL,
	"action" text NOT NULL,
	"target" jsonb NOT NULL,
	"payload" jsonb,
	"ip" text,
	"user_agent" text,
	"prev_hash" text NOT NULL,
	"hash" text NOT NULL,
	"integrity" jsonb,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "export_jobs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"requested_by" text NOT NULL,
	"filters" jsonb NOT NULL,
	"format" text NOT NULL,
	"status" text DEFAULT 'Pending' NOT NULL,
	"file_uri" text,
	"record_count" integer,
	"error" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"finished_at" timestamp with time zone
);
--> statement-breakpoint
CREATE INDEX "ae_tenant_idx" ON "audit_events" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "ae_timestamp_idx" ON "audit_events" USING btree ("timestamp");--> statement-breakpoint
CREATE INDEX "ae_action_idx" ON "audit_events" USING btree ("action");--> statement-breakpoint
CREATE INDEX "ae_hash_idx" ON "audit_events" USING btree ("hash");--> statement-breakpoint
CREATE INDEX "ej_tenant_idx" ON "export_jobs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "ej_status_idx" ON "export_jobs" USING btree ("status");