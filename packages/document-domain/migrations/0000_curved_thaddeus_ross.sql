CREATE TABLE "documents" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"doc_type" text NOT NULL,
	"number" text,
	"template_key" text NOT NULL,
	"template_version" integer NOT NULL,
	"payload_hash" text NOT NULL,
	"locale" text DEFAULT 'de-DE' NOT NULL,
	"status" text DEFAULT 'Draft' NOT NULL,
	"files" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"signatures" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"metadata" jsonb,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "number_series" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"scope" text NOT NULL,
	"pattern" text NOT NULL,
	"next_seq" integer DEFAULT 1 NOT NULL,
	"reset_policy" text DEFAULT 'Yearly' NOT NULL,
	"last_reset_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "templates" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"key" text NOT NULL,
	"name" text NOT NULL,
	"engine" text DEFAULT 'handlebars' NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	"status" text DEFAULT 'Draft' NOT NULL,
	"locale" jsonb DEFAULT '["de-DE"]'::jsonb NOT NULL,
	"paper" text DEFAULT 'A4' NOT NULL,
	"margins" jsonb,
	"source_html" text NOT NULL,
	"css" text,
	"assets" jsonb,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE INDEX "doc_tenant_idx" ON "documents" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "doc_type_idx" ON "documents" USING btree ("doc_type");--> statement-breakpoint
CREATE INDEX "doc_number_idx" ON "documents" USING btree ("number");--> statement-breakpoint
CREATE INDEX "ns_tenant_idx" ON "number_series" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "ns_scope_idx" ON "number_series" USING btree ("scope");--> statement-breakpoint
CREATE INDEX "tpl_tenant_idx" ON "templates" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "tpl_key_idx" ON "templates" USING btree ("key");