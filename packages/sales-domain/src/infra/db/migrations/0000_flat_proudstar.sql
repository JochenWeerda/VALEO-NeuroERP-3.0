CREATE TABLE IF NOT EXISTS "credit_notes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"customer_id" uuid NOT NULL,
	"invoice_id" uuid NOT NULL,
	"credit_number" text NOT NULL,
	"lines" jsonb NOT NULL,
	"subtotal_net" numeric(15, 2) NOT NULL,
	"total_discount" numeric(15, 2) NOT NULL,
	"total_net" numeric(15, 2) NOT NULL,
	"total_gross" numeric(15, 2) NOT NULL,
	"tax_rate" numeric(5, 2) DEFAULT '19.00' NOT NULL,
	"currency" varchar(3) DEFAULT 'EUR' NOT NULL,
	"reason" text NOT NULL,
	"notes" text,
	"status" text DEFAULT 'Issued' NOT NULL,
	"settled_at" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	CONSTRAINT "credit_notes_credit_number_unique" UNIQUE("credit_number")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "invoices" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"customer_id" uuid NOT NULL,
	"order_id" uuid,
	"invoice_number" text NOT NULL,
	"lines" jsonb NOT NULL,
	"subtotal_net" numeric(15, 2) NOT NULL,
	"total_discount" numeric(15, 2) NOT NULL,
	"total_net" numeric(15, 2) NOT NULL,
	"total_gross" numeric(15, 2) NOT NULL,
	"tax_rate" numeric(5, 2) DEFAULT '19.00' NOT NULL,
	"currency" varchar(3) DEFAULT 'EUR' NOT NULL,
	"due_date" timestamp NOT NULL,
	"paid_at" timestamp,
	"notes" text,
	"status" text DEFAULT 'Issued' NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	CONSTRAINT "invoices_invoice_number_unique" UNIQUE("invoice_number")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "orders" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"customer_id" uuid NOT NULL,
	"order_number" text NOT NULL,
	"lines" jsonb NOT NULL,
	"subtotal_net" numeric(15, 2) NOT NULL,
	"total_discount" numeric(15, 2) NOT NULL,
	"total_net" numeric(15, 2) NOT NULL,
	"total_gross" numeric(15, 2) NOT NULL,
	"tax_rate" numeric(5, 2) DEFAULT '19.00' NOT NULL,
	"currency" varchar(3) DEFAULT 'EUR' NOT NULL,
	"expected_delivery_date" timestamp,
	"notes" text,
	"status" text DEFAULT 'Draft' NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	CONSTRAINT "orders_order_number_unique" UNIQUE("order_number")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "quotes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"customer_id" uuid NOT NULL,
	"quote_number" text NOT NULL,
	"lines" jsonb NOT NULL,
	"subtotal_net" numeric(15, 2) NOT NULL,
	"total_discount" numeric(15, 2) NOT NULL,
	"total_net" numeric(15, 2) NOT NULL,
	"total_gross" numeric(15, 2) NOT NULL,
	"tax_rate" numeric(5, 2) DEFAULT '19.00' NOT NULL,
	"currency" varchar(3) DEFAULT 'EUR' NOT NULL,
	"valid_until" timestamp NOT NULL,
	"notes" text,
	"status" text DEFAULT 'Draft' NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	CONSTRAINT "quotes_quote_number_unique" UNIQUE("quote_number")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "sales_offers" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"customer_inquiry_id" uuid,
	"customer_id" uuid NOT NULL,
	"offer_number" text NOT NULL,
	"subject" text NOT NULL,
	"description" text NOT NULL,
	"total_amount" numeric(15, 2) NOT NULL,
	"currency" varchar(3) DEFAULT 'EUR' NOT NULL,
	"valid_until" timestamp NOT NULL,
	"status" text DEFAULT 'ENTWURF' NOT NULL,
	"contact_person" text,
	"delivery_date" timestamp,
	"payment_terms" text,
	"notes" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"deleted_at" timestamp,
	"version" integer DEFAULT 1 NOT NULL,
	CONSTRAINT "sales_offers_offer_number_unique" UNIQUE("offer_number")
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "credit_notes" ADD CONSTRAINT "credit_notes_invoice_id_invoices_id_fk" FOREIGN KEY ("invoice_id") REFERENCES "public"."invoices"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "invoices" ADD CONSTRAINT "invoices_order_id_orders_id_fk" FOREIGN KEY ("order_id") REFERENCES "public"."orders"("id") ON DELETE set null ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "credit_notes_tenant_idx" ON "credit_notes" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "credit_notes_customer_idx" ON "credit_notes" USING btree ("customer_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "credit_notes_invoice_idx" ON "credit_notes" USING btree ("invoice_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "credit_notes_status_idx" ON "credit_notes" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "invoices_tenant_idx" ON "invoices" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "invoices_customer_idx" ON "invoices" USING btree ("customer_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "invoices_order_idx" ON "invoices" USING btree ("order_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "invoices_status_idx" ON "invoices" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "invoices_due_date_idx" ON "invoices" USING btree ("due_date");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "orders_tenant_idx" ON "orders" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "orders_customer_idx" ON "orders" USING btree ("customer_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "orders_status_idx" ON "orders" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "orders_delivery_date_idx" ON "orders" USING btree ("expected_delivery_date");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "quotes_tenant_idx" ON "quotes" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "quotes_customer_idx" ON "quotes" USING btree ("customer_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "quotes_status_idx" ON "quotes" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "quotes_valid_until_idx" ON "quotes" USING btree ("valid_until");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "sales_offers_tenant_idx" ON "sales_offers" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "sales_offers_customer_idx" ON "sales_offers" USING btree ("customer_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "sales_offers_customer_inquiry_idx" ON "sales_offers" USING btree ("customer_inquiry_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "sales_offers_status_idx" ON "sales_offers" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "sales_offers_valid_until_idx" ON "sales_offers" USING btree ("valid_until");