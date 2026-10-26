CREATE TABLE "condition_sets" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"key" text NOT NULL,
	"key_type" text NOT NULL,
	"rules" jsonb NOT NULL,
	"priority" integer DEFAULT 100 NOT NULL,
	"conflict_strategy" text DEFAULT 'Stack' NOT NULL,
	"valid_from" timestamp with time zone NOT NULL,
	"valid_to" timestamp with time zone,
	"active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by" text,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_by" text
);
--> statement-breakpoint
CREATE TABLE "dynamic_formulas" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"expression" text NOT NULL,
	"inputs" jsonb NOT NULL,
	"rounding" jsonb,
	"caps" jsonb,
	"sku" text,
	"commodity" text,
	"valid_from" timestamp with time zone NOT NULL,
	"valid_to" timestamp with time zone,
	"active" boolean DEFAULT true NOT NULL,
	"test_inputs" jsonb,
	"expected_result" numeric(15, 4),
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by" text,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_by" text
);
--> statement-breakpoint
CREATE TABLE "price_lists" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"code" text,
	"currency" text DEFAULT 'EUR' NOT NULL,
	"valid_from" timestamp with time zone NOT NULL,
	"valid_to" timestamp with time zone,
	"lines" jsonb NOT NULL,
	"status" text DEFAULT 'Draft' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by" text,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_by" text,
	"activated_at" timestamp with time zone,
	"activated_by" text
);
--> statement-breakpoint
CREATE TABLE "price_quotes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"inputs" jsonb NOT NULL,
	"components" jsonb NOT NULL,
	"total_net" numeric(15, 2) NOT NULL,
	"total_gross" numeric(15, 2),
	"currency" text DEFAULT 'EUR' NOT NULL,
	"calculated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"expires_at" timestamp with time zone NOT NULL,
	"signature" text,
	"created_by" text
);
--> statement-breakpoint
CREATE TABLE "tax_charge_refs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"code" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"type" text NOT NULL,
	"method" text NOT NULL,
	"rate_or_amount" numeric(10, 4) NOT NULL,
	"scope" text NOT NULL,
	"scope_value" text,
	"valid_from" timestamp with time zone NOT NULL,
	"valid_to" timestamp with time zone,
	"country" text DEFAULT 'DE' NOT NULL,
	"region" text,
	"active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by" text,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_by" text
);
--> statement-breakpoint
CREATE INDEX "cs_tenant_idx" ON "condition_sets" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "cs_key_idx" ON "condition_sets" USING btree ("key");--> statement-breakpoint
CREATE INDEX "cs_active_idx" ON "condition_sets" USING btree ("active");--> statement-breakpoint
CREATE INDEX "df_tenant_idx" ON "dynamic_formulas" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "df_sku_idx" ON "dynamic_formulas" USING btree ("sku");--> statement-breakpoint
CREATE INDEX "df_commodity_idx" ON "dynamic_formulas" USING btree ("commodity");--> statement-breakpoint
CREATE INDEX "df_active_idx" ON "dynamic_formulas" USING btree ("active");--> statement-breakpoint
CREATE INDEX "pl_tenant_idx" ON "price_lists" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "pl_status_idx" ON "price_lists" USING btree ("status");--> statement-breakpoint
CREATE INDEX "pl_valid_from_idx" ON "price_lists" USING btree ("valid_from");--> statement-breakpoint
CREATE INDEX "pq_tenant_idx" ON "price_quotes" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "pq_expires_at_idx" ON "price_quotes" USING btree ("expires_at");--> statement-breakpoint
CREATE INDEX "tc_tenant_idx" ON "tax_charge_refs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "tc_code_idx" ON "tax_charge_refs" USING btree ("code");--> statement-breakpoint
CREATE INDEX "tc_type_idx" ON "tax_charge_refs" USING btree ("type");--> statement-breakpoint
CREATE INDEX "tc_active_idx" ON "tax_charge_refs" USING btree ("active");