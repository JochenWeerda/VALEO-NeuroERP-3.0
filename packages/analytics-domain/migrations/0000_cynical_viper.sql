CREATE TABLE "fact_contracts" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"event_id" text NOT NULL,
	"event_type" text NOT NULL,
	"occurred_at" timestamp NOT NULL,
	"contract_id" text NOT NULL,
	"customer_id" text,
	"supplier_id" text,
	"commodity" text NOT NULL,
	"quantity" numeric(15, 3),
	"unit" text,
	"price" numeric(10, 4),
	"currency" text DEFAULT 'EUR',
	"status" text,
	"delivery_start" timestamp,
	"delivery_end" timestamp,
	"contract_type" text,
	"hedging_required" boolean DEFAULT false,
	"metadata" jsonb
);
--> statement-breakpoint
CREATE TABLE "fact_finance" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"event_id" text NOT NULL,
	"event_type" text NOT NULL,
	"occurred_at" timestamp NOT NULL,
	"invoice_id" text,
	"contract_id" text,
	"customer_id" text,
	"supplier_id" text,
	"commodity" text,
	"amount" numeric(15, 2),
	"currency" text DEFAULT 'EUR',
	"type" text,
	"status" text,
	"due_date" timestamp,
	"paid_date" timestamp,
	"metadata" jsonb
);
--> statement-breakpoint
CREATE TABLE "fact_production" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"event_id" text NOT NULL,
	"event_type" text NOT NULL,
	"occurred_at" timestamp NOT NULL,
	"batch_id" text NOT NULL,
	"contract_id" text,
	"commodity" text NOT NULL,
	"quantity" numeric(15, 3),
	"unit" text,
	"quality_grade" text,
	"moisture" numeric(5, 2),
	"protein" numeric(5, 2),
	"status" text,
	"site_id" text,
	"metadata" jsonb
);
--> statement-breakpoint
CREATE TABLE "fact_quality" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"event_id" text NOT NULL,
	"event_type" text NOT NULL,
	"occurred_at" timestamp NOT NULL,
	"sample_id" text NOT NULL,
	"batch_id" text,
	"contract_id" text,
	"commodity" text NOT NULL,
	"test_type" text,
	"test_result" text,
	"numeric_result" numeric(10, 4),
	"unit" text,
	"is_passed" boolean,
	"tested_by" text,
	"site_id" text,
	"metadata" jsonb
);
--> statement-breakpoint
CREATE TABLE "fact_regulatory" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"event_id" text NOT NULL,
	"event_type" text NOT NULL,
	"occurred_at" timestamp NOT NULL,
	"batch_id" text,
	"contract_id" text,
	"commodity" text NOT NULL,
	"label_type" text,
	"is_eligible" boolean,
	"certification_number" text,
	"expiry_date" timestamp,
	"issued_by" text,
	"site_id" text,
	"metadata" jsonb
);
--> statement-breakpoint
CREATE TABLE "fact_weighing" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"event_id" text NOT NULL,
	"event_type" text NOT NULL,
	"occurred_at" timestamp NOT NULL,
	"ticket_id" text NOT NULL,
	"contract_id" text,
	"order_id" text,
	"customer_id" text,
	"commodity" text NOT NULL,
	"gross_weight" numeric(10, 3),
	"tare_weight" numeric(10, 3),
	"net_weight" numeric(10, 3),
	"unit" text DEFAULT 'kg',
	"tolerance_percent" numeric(5, 2),
	"is_within_tolerance" boolean,
	"status" text,
	"site_id" text,
	"gate_id" text,
	"license_plate" text,
	"metadata" jsonb
);
--> statement-breakpoint
CREATE TABLE "forecasts" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	"metric_name" text NOT NULL,
	"horizon" integer NOT NULL,
	"horizon_unit" text NOT NULL,
	"model" text NOT NULL,
	"forecast_values" jsonb NOT NULL,
	"confidence_interval" numeric(3, 2),
	"metadata" jsonb
);
--> statement-breakpoint
CREATE TABLE "kpis" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	"name" text NOT NULL,
	"description" text NOT NULL,
	"value" text NOT NULL,
	"unit" text NOT NULL,
	"context" jsonb,
	"calculated_at" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb
);
--> statement-breakpoint
CREATE TABLE "mv_contract_positions" (
	"tenant_id" text NOT NULL,
	"commodity" text NOT NULL,
	"month" text NOT NULL,
	"short_position" numeric(15, 3) DEFAULT '0',
	"long_position" numeric(15, 3) DEFAULT '0',
	"net_position" numeric(15, 3) DEFAULT '0',
	"hedging_ratio" numeric(5, 4),
	"last_updated" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "mv_finance_kpis" (
	"tenant_id" text NOT NULL,
	"commodity" text,
	"customer_id" text,
	"period" text NOT NULL,
	"total_revenue" numeric(15, 2) DEFAULT '0',
	"total_cost" numeric(15, 2) DEFAULT '0',
	"gross_margin" numeric(15, 2) DEFAULT '0',
	"margin_percentage" numeric(5, 4),
	"outstanding_invoices" numeric(15, 2) DEFAULT '0',
	"overdue_invoices" numeric(15, 2) DEFAULT '0',
	"last_updated" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "mv_inventory_balances" (
	"tenant_id" text NOT NULL,
	"commodity" text NOT NULL,
	"site_id" text,
	"current_balance" numeric(15, 3) DEFAULT '0',
	"reserved_balance" numeric(15, 3) DEFAULT '0',
	"available_balance" numeric(15, 3) DEFAULT '0',
	"last_updated" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "mv_quality_stats" (
	"tenant_id" text NOT NULL,
	"commodity" text NOT NULL,
	"period" text NOT NULL,
	"total_samples" integer DEFAULT 0,
	"passed_samples" integer DEFAULT 0,
	"failed_samples" integer DEFAULT 0,
	"pass_rate" numeric(5, 4),
	"failure_rate" numeric(5, 4),
	"avg_moisture" numeric(5, 2),
	"avg_protein" numeric(5, 2),
	"last_updated" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "mv_regulatory_stats" (
	"tenant_id" text NOT NULL,
	"commodity" text NOT NULL,
	"label_type" text NOT NULL,
	"period" text NOT NULL,
	"total_eligible" integer DEFAULT 0,
	"total_ineligible" integer DEFAULT 0,
	"eligibility_rate" numeric(5, 4),
	"ineligibility_rate" numeric(5, 4),
	"last_updated" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "mv_weighing_volumes" (
	"tenant_id" text NOT NULL,
	"commodity" text NOT NULL,
	"customer_id" text,
	"site_id" text,
	"period" text NOT NULL,
	"total_weight" numeric(15, 3) DEFAULT '0',
	"total_tickets" integer DEFAULT 0,
	"avg_weight" numeric(10, 3),
	"within_tolerance" integer DEFAULT 0,
	"outside_tolerance" integer DEFAULT 0,
	"last_updated" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "reports" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL,
	"type" text NOT NULL,
	"parameters" jsonb NOT NULL,
	"generated_at" timestamp DEFAULT now() NOT NULL,
	"uri" text,
	"format" text DEFAULT 'json' NOT NULL,
	"metadata" jsonb
);
--> statement-breakpoint
CREATE INDEX "fact_contracts_tenant_event_idx" ON "fact_contracts" USING btree ("tenant_id","event_id");--> statement-breakpoint
CREATE INDEX "fact_contracts_tenant_commodity_idx" ON "fact_contracts" USING btree ("tenant_id","commodity");--> statement-breakpoint
CREATE INDEX "fact_contracts_tenant_status_idx" ON "fact_contracts" USING btree ("tenant_id","status");--> statement-breakpoint
CREATE INDEX "fact_contracts_tenant_occurred_idx" ON "fact_contracts" USING btree ("tenant_id","occurred_at");--> statement-breakpoint
CREATE INDEX "fact_finance_tenant_event_idx" ON "fact_finance" USING btree ("tenant_id","event_id");--> statement-breakpoint
CREATE INDEX "fact_finance_tenant_invoice_idx" ON "fact_finance" USING btree ("tenant_id","invoice_id");--> statement-breakpoint
CREATE INDEX "fact_finance_tenant_customer_idx" ON "fact_finance" USING btree ("tenant_id","customer_id");--> statement-breakpoint
CREATE INDEX "fact_finance_tenant_status_idx" ON "fact_finance" USING btree ("tenant_id","status");--> statement-breakpoint
CREATE INDEX "fact_finance_tenant_occurred_idx" ON "fact_finance" USING btree ("tenant_id","occurred_at");--> statement-breakpoint
CREATE INDEX "fact_production_tenant_event_idx" ON "fact_production" USING btree ("tenant_id","event_id");--> statement-breakpoint
CREATE INDEX "fact_production_tenant_batch_idx" ON "fact_production" USING btree ("tenant_id","batch_id");--> statement-breakpoint
CREATE INDEX "fact_production_tenant_commodity_idx" ON "fact_production" USING btree ("tenant_id","commodity");--> statement-breakpoint
CREATE INDEX "fact_production_tenant_occurred_idx" ON "fact_production" USING btree ("tenant_id","occurred_at");--> statement-breakpoint
CREATE INDEX "fact_quality_tenant_event_idx" ON "fact_quality" USING btree ("tenant_id","event_id");--> statement-breakpoint
CREATE INDEX "fact_quality_tenant_sample_idx" ON "fact_quality" USING btree ("tenant_id","sample_id");--> statement-breakpoint
CREATE INDEX "fact_quality_tenant_commodity_idx" ON "fact_quality" USING btree ("tenant_id","commodity");--> statement-breakpoint
CREATE INDEX "fact_quality_tenant_passed_idx" ON "fact_quality" USING btree ("tenant_id","is_passed");--> statement-breakpoint
CREATE INDEX "fact_quality_tenant_occurred_idx" ON "fact_quality" USING btree ("tenant_id","occurred_at");--> statement-breakpoint
CREATE INDEX "fact_regulatory_tenant_event_idx" ON "fact_regulatory" USING btree ("tenant_id","event_id");--> statement-breakpoint
CREATE INDEX "fact_regulatory_tenant_batch_idx" ON "fact_regulatory" USING btree ("tenant_id","batch_id");--> statement-breakpoint
CREATE INDEX "fact_regulatory_tenant_commodity_idx" ON "fact_regulatory" USING btree ("tenant_id","commodity");--> statement-breakpoint
CREATE INDEX "fact_regulatory_tenant_eligible_idx" ON "fact_regulatory" USING btree ("tenant_id","is_eligible");--> statement-breakpoint
CREATE INDEX "fact_regulatory_tenant_occurred_idx" ON "fact_regulatory" USING btree ("tenant_id","occurred_at");--> statement-breakpoint
CREATE INDEX "fact_weighing_tenant_event_idx" ON "fact_weighing" USING btree ("tenant_id","event_id");--> statement-breakpoint
CREATE INDEX "fact_weighing_tenant_ticket_idx" ON "fact_weighing" USING btree ("tenant_id","ticket_id");--> statement-breakpoint
CREATE INDEX "fact_weighing_tenant_commodity_idx" ON "fact_weighing" USING btree ("tenant_id","commodity");--> statement-breakpoint
CREATE INDEX "fact_weighing_tenant_status_idx" ON "fact_weighing" USING btree ("tenant_id","status");--> statement-breakpoint
CREATE INDEX "fact_weighing_tenant_occurred_idx" ON "fact_weighing" USING btree ("tenant_id","occurred_at");--> statement-breakpoint
CREATE INDEX "forecasts_tenant_metric_idx" ON "forecasts" USING btree ("tenant_id","metric_name");--> statement-breakpoint
CREATE INDEX "forecasts_tenant_created_idx" ON "forecasts" USING btree ("tenant_id","created_at");--> statement-breakpoint
CREATE INDEX "kpis_tenant_name_idx" ON "kpis" USING btree ("tenant_id","name");--> statement-breakpoint
CREATE INDEX "kpis_tenant_calculated_idx" ON "kpis" USING btree ("tenant_id","calculated_at");--> statement-breakpoint
CREATE INDEX "mv_contract_positions_tenant_commodity_month_idx" ON "mv_contract_positions" USING btree ("tenant_id","commodity","month");--> statement-breakpoint
CREATE INDEX "mv_finance_kpis_tenant_commodity_period_idx" ON "mv_finance_kpis" USING btree ("tenant_id","commodity","period");--> statement-breakpoint
CREATE INDEX "mv_inventory_balances_tenant_commodity_idx" ON "mv_inventory_balances" USING btree ("tenant_id","commodity");--> statement-breakpoint
CREATE INDEX "mv_quality_stats_tenant_commodity_period_idx" ON "mv_quality_stats" USING btree ("tenant_id","commodity","period");--> statement-breakpoint
CREATE INDEX "mv_regulatory_stats_tenant_commodity_label_period_idx" ON "mv_regulatory_stats" USING btree ("tenant_id","commodity","label_type","period");--> statement-breakpoint
CREATE INDEX "mv_weighing_volumes_tenant_commodity_period_idx" ON "mv_weighing_volumes" USING btree ("tenant_id","commodity","period");--> statement-breakpoint
CREATE INDEX "reports_tenant_type_idx" ON "reports" USING btree ("tenant_id","type");--> statement-breakpoint
CREATE INDEX "reports_tenant_generated_idx" ON "reports" USING btree ("tenant_id","generated_at");