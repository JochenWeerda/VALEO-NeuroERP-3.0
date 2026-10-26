CREATE TABLE "capas" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"linked_nc_ids" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"capa_number" text NOT NULL,
	"type" text NOT NULL,
	"title" text NOT NULL,
	"description" text NOT NULL,
	"action" text NOT NULL,
	"root_cause_analysis" text,
	"prevention_strategy" text,
	"responsible_user_id" text NOT NULL,
	"responsible_department" text,
	"team_members" jsonb,
	"due_date" timestamp with time zone NOT NULL,
	"implemented_at" timestamp with time zone,
	"verified_at" timestamp with time zone,
	"status" text DEFAULT 'Open' NOT NULL,
	"effectiveness_check" boolean,
	"effectiveness_comment" text,
	"verified_by" text,
	"verification_method" text,
	"verification_result" text,
	"estimated_cost" numeric(15, 2),
	"actual_cost" numeric(15, 2),
	"escalated" boolean DEFAULT false NOT NULL,
	"escalated_to" text,
	"escalated_at" timestamp with time zone,
	"escalation_reason" text,
	"closed_at" timestamp with time zone,
	"closed_by" text,
	"closure_comment" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by" text,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_by" text,
	CONSTRAINT "capas_capa_number_unique" UNIQUE("capa_number")
);
--> statement-breakpoint
CREATE TABLE "non_conformities" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"batch_id" uuid,
	"contract_id" uuid,
	"sample_id" uuid,
	"lot_id" uuid,
	"supplier_id" uuid,
	"nc_number" text NOT NULL,
	"type" text NOT NULL,
	"severity" text NOT NULL,
	"title" text NOT NULL,
	"description" text NOT NULL,
	"root_cause" text,
	"detected_at" timestamp with time zone NOT NULL,
	"detected_by" text NOT NULL,
	"detected_location" text,
	"assigned_to" text,
	"responsible_department" text,
	"status" text DEFAULT 'Open' NOT NULL,
	"immediate_action" text,
	"capa_id" uuid,
	"estimated_cost" numeric(15, 2),
	"actual_cost" numeric(15, 2),
	"affected_quantity" numeric(15, 3),
	"affected_unit" text,
	"closed_at" timestamp with time zone,
	"closed_by" text,
	"verified_at" timestamp with time zone,
	"verified_by" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "non_conformities_nc_number_unique" UNIQUE("nc_number")
);
--> statement-breakpoint
CREATE TABLE "quality_plans" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"commodity" text,
	"contract_id" uuid,
	"production_context" text,
	"active" boolean DEFAULT true NOT NULL,
	"rules" jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by" text,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_by" text,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sample_results" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"sample_id" uuid NOT NULL,
	"analyte" text NOT NULL,
	"value" numeric(15, 6) NOT NULL,
	"unit" text NOT NULL,
	"method" text NOT NULL,
	"lab_id" text,
	"analyzed_at" timestamp with time zone,
	"analyzed_by" text,
	"result" text NOT NULL,
	"limits" jsonb,
	"comment" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "samples" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"batch_id" uuid,
	"contract_id" uuid,
	"lot_id" uuid,
	"source" text NOT NULL,
	"sample_code" text NOT NULL,
	"description" text,
	"taken_at" timestamp with time zone NOT NULL,
	"taken_by" text NOT NULL,
	"taken_location" text,
	"plan_id" uuid,
	"retained" boolean DEFAULT false NOT NULL,
	"retained_location" text,
	"retained_until" timestamp with time zone,
	"status" text DEFAULT 'Pending' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"disposed_at" timestamp with time zone,
	"disposed_by" text
);
--> statement-breakpoint
ALTER TABLE "sample_results" ADD CONSTRAINT "sample_results_sample_id_samples_id_fk" FOREIGN KEY ("sample_id") REFERENCES "public"."samples"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "capa_tenant_idx" ON "capas" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "capa_number_idx" ON "capas" USING btree ("capa_number");--> statement-breakpoint
CREATE INDEX "capa_status_idx" ON "capas" USING btree ("status");--> statement-breakpoint
CREATE INDEX "capa_responsible_idx" ON "capas" USING btree ("responsible_user_id");--> statement-breakpoint
CREATE INDEX "capa_due_date_idx" ON "capas" USING btree ("due_date");--> statement-breakpoint
CREATE INDEX "nc_tenant_idx" ON "non_conformities" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "nc_number_idx" ON "non_conformities" USING btree ("nc_number");--> statement-breakpoint
CREATE INDEX "nc_batch_idx" ON "non_conformities" USING btree ("batch_id");--> statement-breakpoint
CREATE INDEX "nc_contract_idx" ON "non_conformities" USING btree ("contract_id");--> statement-breakpoint
CREATE INDEX "nc_status_idx" ON "non_conformities" USING btree ("status");--> statement-breakpoint
CREATE INDEX "nc_severity_idx" ON "non_conformities" USING btree ("severity");--> statement-breakpoint
CREATE INDEX "nc_detected_at_idx" ON "non_conformities" USING btree ("detected_at");--> statement-breakpoint
CREATE INDEX "qp_tenant_idx" ON "quality_plans" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "qp_commodity_idx" ON "quality_plans" USING btree ("commodity");--> statement-breakpoint
CREATE INDEX "qp_contract_idx" ON "quality_plans" USING btree ("contract_id");--> statement-breakpoint
CREATE INDEX "qp_active_idx" ON "quality_plans" USING btree ("active");--> statement-breakpoint
CREATE INDEX "sr_tenant_idx" ON "sample_results" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "sr_sample_idx" ON "sample_results" USING btree ("sample_id");--> statement-breakpoint
CREATE INDEX "sr_analyte_idx" ON "sample_results" USING btree ("analyte");--> statement-breakpoint
CREATE INDEX "sr_result_idx" ON "sample_results" USING btree ("result");--> statement-breakpoint
CREATE INDEX "sample_tenant_idx" ON "samples" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "sample_batch_idx" ON "samples" USING btree ("batch_id");--> statement-breakpoint
CREATE INDEX "sample_contract_idx" ON "samples" USING btree ("contract_id");--> statement-breakpoint
CREATE INDEX "sample_lot_idx" ON "samples" USING btree ("lot_id");--> statement-breakpoint
CREATE INDEX "sample_code_idx" ON "samples" USING btree ("sample_code");--> statement-breakpoint
CREATE INDEX "sample_status_idx" ON "samples" USING btree ("status");--> statement-breakpoint
CREATE INDEX "sample_taken_at_idx" ON "samples" USING btree ("taken_at");