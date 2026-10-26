CREATE TABLE "contacts" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"customer_id" uuid NOT NULL,
	"first_name" text NOT NULL,
	"last_name" text NOT NULL,
	"role" text,
	"email" text NOT NULL,
	"phone" text,
	"is_primary" boolean DEFAULT false NOT NULL,
	"notes" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "customers" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"number" text NOT NULL,
	"name" text NOT NULL,
	"vat_id" text,
	"billing_address" jsonb NOT NULL,
	"shipping_addresses" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"email" text,
	"phone" text,
	"tags" text[] DEFAULT '{}' NOT NULL,
	"status" text DEFAULT 'Prospect' NOT NULL,
	"owner_user_id" uuid,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	CONSTRAINT "customers_number_unique" UNIQUE("number")
);
--> statement-breakpoint
CREATE TABLE "interactions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"customer_id" uuid NOT NULL,
	"contact_id" uuid,
	"type" text NOT NULL,
	"subject" text NOT NULL,
	"content" text NOT NULL,
	"occurred_at" timestamp NOT NULL,
	"created_by" uuid NOT NULL,
	"attachments" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "opportunities" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"customer_id" uuid NOT NULL,
	"title" text NOT NULL,
	"stage" text DEFAULT 'Lead' NOT NULL,
	"expected_close_date" timestamp,
	"amount_net" numeric(15, 2),
	"currency" text,
	"probability" numeric(3, 2) DEFAULT '0.10' NOT NULL,
	"owner_user_id" uuid,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
ALTER TABLE "contacts" ADD CONSTRAINT "contacts_customer_id_customers_id_fk" FOREIGN KEY ("customer_id") REFERENCES "public"."customers"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "interactions" ADD CONSTRAINT "interactions_customer_id_customers_id_fk" FOREIGN KEY ("customer_id") REFERENCES "public"."customers"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "interactions" ADD CONSTRAINT "interactions_contact_id_contacts_id_fk" FOREIGN KEY ("contact_id") REFERENCES "public"."contacts"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "opportunities" ADD CONSTRAINT "opportunities_customer_id_customers_id_fk" FOREIGN KEY ("customer_id") REFERENCES "public"."customers"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "contacts_tenant_idx" ON "contacts" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "contacts_customer_idx" ON "contacts" USING btree ("customer_id");--> statement-breakpoint
CREATE INDEX "contacts_email_idx" ON "contacts" USING btree ("email");--> statement-breakpoint
CREATE INDEX "contacts_primary_idx" ON "contacts" USING btree ("customer_id","is_primary");--> statement-breakpoint
CREATE INDEX "customers_tenant_idx" ON "customers" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "customers_status_idx" ON "customers" USING btree ("status");--> statement-breakpoint
CREATE INDEX "customers_owner_idx" ON "customers" USING btree ("owner_user_id");--> statement-breakpoint
CREATE INDEX "interactions_tenant_idx" ON "interactions" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "interactions_customer_idx" ON "interactions" USING btree ("customer_id");--> statement-breakpoint
CREATE INDEX "interactions_contact_idx" ON "interactions" USING btree ("contact_id");--> statement-breakpoint
CREATE INDEX "interactions_type_idx" ON "interactions" USING btree ("type");--> statement-breakpoint
CREATE INDEX "interactions_occurred_at_idx" ON "interactions" USING btree ("occurred_at");--> statement-breakpoint
CREATE INDEX "interactions_created_by_idx" ON "interactions" USING btree ("created_by");--> statement-breakpoint
CREATE INDEX "opportunities_tenant_idx" ON "opportunities" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "opportunities_customer_idx" ON "opportunities" USING btree ("customer_id");--> statement-breakpoint
CREATE INDEX "opportunities_stage_idx" ON "opportunities" USING btree ("stage");--> statement-breakpoint
CREATE INDEX "opportunities_owner_idx" ON "opportunities" USING btree ("owner_user_id");--> statement-breakpoint
CREATE INDEX "opportunities_amount_idx" ON "opportunities" USING btree ("amount_net");