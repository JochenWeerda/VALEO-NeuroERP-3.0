CREATE TABLE "compliance_cases" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"case_number" text NOT NULL,
	"type" text NOT NULL,
	"severity" text NOT NULL,
	"ref" jsonb NOT NULL,
	"title" text NOT NULL,
	"description" text NOT NULL,
	"policy_id" uuid,
	"label_code" text,
	"rule_id" text,
	"detected_at" timestamp with time zone NOT NULL,
	"detected_by" text NOT NULL,
	"detection_method" text,
	"status" text DEFAULT 'Open' NOT NULL,
	"immediate_action" text,
	"capa_id" uuid,
	"impacted_batches" jsonb,
	"impacted_labels" jsonb,
	"resolved_at" timestamp with time zone,
	"resolved_by" text,
	"resolution" text,
	"closed_at" timestamp with time zone,
	"closed_by" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "compliance_cases_case_number_unique" UNIQUE("case_number")
);
--> statement-breakpoint
CREATE TABLE "evidences" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"type" text NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"uri" text,
	"hash" text,
	"mime_type" text,
	"file_size" numeric,
	"issued_by" text NOT NULL,
	"issued_at" timestamp with time zone NOT NULL,
	"valid_from" timestamp with time zone,
	"valid_to" timestamp with time zone,
	"status" text DEFAULT 'Valid' NOT NULL,
	"related_ref" jsonb,
	"supporting_labels" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"supporting_policies" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by" text,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "ghg_pathways" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"commodity" text NOT NULL,
	"pathway_key" text NOT NULL,
	"description" text,
	"method" text NOT NULL,
	"standard" text DEFAULT 'REDII' NOT NULL,
	"factors" jsonb NOT NULL,
	"total_emissions" numeric(10, 2) NOT NULL,
	"emissions_per_ton" numeric(10, 2),
	"savings_vs_fossil" numeric(5, 2),
	"redii_threshold" numeric(5, 2),
	"redii_compliant" boolean,
	"data_sources" jsonb,
	"calculated_at" timestamp with time zone,
	"calculated_by" text,
	"valid_from" timestamp with time zone,
	"valid_to" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "labels" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"code" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"target_type" text NOT NULL,
	"target_id" text NOT NULL,
	"status" text DEFAULT 'Pending' NOT NULL,
	"evidence_refs" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"missing_evidences" jsonb,
	"issued_at" timestamp with time zone,
	"issued_by" text,
	"valid_from" timestamp with time zone,
	"valid_to" timestamp with time zone,
	"revoked_at" timestamp with time zone,
	"revoked_by" text,
	"revoked_reason" text,
	"policy_id" uuid,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "psm_product_refs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"bvl_id" text,
	"name" text NOT NULL,
	"active_substances" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"approval_status" text DEFAULT 'Unknown' NOT NULL,
	"approval_valid_to" timestamp with time zone,
	"approval_number" text,
	"usage_scope" text,
	"restrictions" jsonb,
	"last_checked_at" timestamp with time zone,
	"last_checked_by" text,
	"source_url" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "regulatory_policies" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" text NOT NULL,
	"key" text NOT NULL,
	"version" text DEFAULT '1.0' NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"scope" text NOT NULL,
	"scope_value" text,
	"rules" jsonb NOT NULL,
	"active" boolean DEFAULT true NOT NULL,
	"valid_from" timestamp with time zone NOT NULL,
	"valid_to" timestamp with time zone,
	"standard_reference" text,
	"legal_basis" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by" text,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_by" text
);
--> statement-breakpoint
CREATE INDEX "cc_tenant_idx" ON "compliance_cases" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "cc_case_number_idx" ON "compliance_cases" USING btree ("case_number");--> statement-breakpoint
CREATE INDEX "cc_type_idx" ON "compliance_cases" USING btree ("type");--> statement-breakpoint
CREATE INDEX "cc_status_idx" ON "compliance_cases" USING btree ("status");--> statement-breakpoint
CREATE INDEX "cc_severity_idx" ON "compliance_cases" USING btree ("severity");--> statement-breakpoint
CREATE INDEX "cc_detected_at_idx" ON "compliance_cases" USING btree ("detected_at");--> statement-breakpoint
CREATE INDEX "ev_tenant_idx" ON "evidences" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "ev_type_idx" ON "evidences" USING btree ("type");--> statement-breakpoint
CREATE INDEX "ev_status_idx" ON "evidences" USING btree ("status");--> statement-breakpoint
CREATE INDEX "ev_valid_to_idx" ON "evidences" USING btree ("valid_to");--> statement-breakpoint
CREATE INDEX "ghg_tenant_idx" ON "ghg_pathways" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "ghg_commodity_idx" ON "ghg_pathways" USING btree ("commodity");--> statement-breakpoint
CREATE INDEX "ghg_pathway_idx" ON "ghg_pathways" USING btree ("pathway_key");--> statement-breakpoint
CREATE INDEX "ghg_method_idx" ON "ghg_pathways" USING btree ("method");--> statement-breakpoint
CREATE INDEX "label_tenant_idx" ON "labels" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "label_code_idx" ON "labels" USING btree ("code");--> statement-breakpoint
CREATE INDEX "label_target_idx" ON "labels" USING btree ("target_type","target_id");--> statement-breakpoint
CREATE INDEX "label_status_idx" ON "labels" USING btree ("status");--> statement-breakpoint
CREATE INDEX "psm_tenant_idx" ON "psm_product_refs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "psm_bvl_id_idx" ON "psm_product_refs" USING btree ("bvl_id");--> statement-breakpoint
CREATE INDEX "psm_name_idx" ON "psm_product_refs" USING btree ("name");--> statement-breakpoint
CREATE INDEX "psm_status_idx" ON "psm_product_refs" USING btree ("approval_status");--> statement-breakpoint
CREATE INDEX "rp_tenant_idx" ON "regulatory_policies" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "rp_key_idx" ON "regulatory_policies" USING btree ("key");--> statement-breakpoint
CREATE INDEX "rp_scope_idx" ON "regulatory_policies" USING btree ("scope");--> statement-breakpoint
CREATE INDEX "rp_active_idx" ON "regulatory_policies" USING btree ("active");