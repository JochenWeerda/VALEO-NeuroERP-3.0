CREATE TABLE "anpr_records" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"license_plate" text NOT NULL,
	"confidence" numeric(5, 2) NOT NULL,
	"confidence_level" text NOT NULL,
	"captured_at" timestamp NOT NULL,
	"image_uri" text,
	"camera_id" text NOT NULL,
	"gate_id" text,
	"status" text DEFAULT 'Detected' NOT NULL,
	"processed_at" timestamp,
	"ticket_suggestion_id" uuid,
	"assigned_ticket_id" uuid,
	"vehicle_id" uuid,
	"contract_id" uuid,
	"order_id" uuid,
	"commodity" text,
	"error_message" text,
	"retry_count" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "audit_logs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"entity_type" text NOT NULL,
	"entity_id" uuid NOT NULL,
	"action" text NOT NULL,
	"user_id" uuid,
	"user_role" text,
	"ip_address" text,
	"user_agent" text,
	"old_values" jsonb,
	"new_values" jsonb,
	"changes" jsonb,
	"session_id" uuid,
	"request_id" text,
	"gate_id" text,
	"scale_id" text,
	"timestamp" timestamp DEFAULT now() NOT NULL,
	"notes" text
);
--> statement-breakpoint
CREATE TABLE "report_templates" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"type" text NOT NULL,
	"category" text NOT NULL,
	"config" jsonb NOT NULL,
	"parameters" jsonb,
	"schedule" jsonb,
	"format" text DEFAULT 'CSV' NOT NULL,
	"recipients" jsonb,
	"is_active" boolean DEFAULT true NOT NULL,
	"created_by" uuid NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"last_run_at" timestamp,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "slots" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"gate_id" text NOT NULL,
	"gate_type" text NOT NULL,
	"window_from" timestamp NOT NULL,
	"window_to" timestamp NOT NULL,
	"assigned_vehicle_id" uuid,
	"license_plate" text,
	"priority" integer DEFAULT 5 NOT NULL,
	"status" text DEFAULT 'Scheduled' NOT NULL,
	"contract_id" uuid,
	"order_id" uuid,
	"commodity" text,
	"expected_weight" numeric(10, 2),
	"entered_at" timestamp,
	"exited_at" timestamp,
	"actual_service_start" timestamp,
	"notes" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "wait_logs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"ticket_id" uuid NOT NULL,
	"license_plate" text,
	"arrival_at" timestamp NOT NULL,
	"service_start_at" timestamp,
	"service_end_at" timestamp,
	"wait_time_minutes" integer,
	"service_time_minutes" integer,
	"total_time_minutes" integer,
	"gate_id" text NOT NULL,
	"gate_type" text NOT NULL,
	"slot_id" uuid,
	"priority" integer DEFAULT 5 NOT NULL,
	"is_high_priority" boolean,
	"is_overtime" boolean,
	"contract_id" uuid,
	"order_id" uuid,
	"commodity" text,
	"expected_weight" numeric(10, 2),
	"status" text DEFAULT 'Waiting' NOT NULL,
	"notes" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "weighing_sessions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"session_number" text NOT NULL,
	"gate_id" text NOT NULL,
	"scale_id" text NOT NULL,
	"operator_id" uuid,
	"started_at" timestamp NOT NULL,
	"ended_at" timestamp,
	"total_tickets" integer DEFAULT 0 NOT NULL,
	"total_weight" numeric(12, 2),
	"total_weight_unit" text,
	"status" text DEFAULT 'Active' NOT NULL,
	"notes" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "weighing_tickets" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"ticket_number" text NOT NULL,
	"type" text NOT NULL,
	"status" text DEFAULT 'Draft' NOT NULL,
	"license_plate" text,
	"container_number" text,
	"silo_id" text,
	"commodity" text NOT NULL,
	"commodity_description" text,
	"gross_weight" jsonb,
	"tare_weight" jsonb,
	"net_weight" numeric(10, 2),
	"net_weight_unit" text,
	"expected_weight" numeric(10, 2),
	"tolerance_percent" numeric(5, 2) DEFAULT '2.00' NOT NULL,
	"is_within_tolerance" boolean,
	"contract_id" uuid,
	"order_id" uuid,
	"delivery_note_id" uuid,
	"anpr_record_id" uuid,
	"auto_assigned" boolean DEFAULT false NOT NULL,
	"gate_id" text,
	"slot_id" uuid,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"completed_at" timestamp,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE INDEX "anpr_records_tenant_idx" ON "anpr_records" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "anpr_records_license_plate_idx" ON "anpr_records" USING btree ("license_plate");--> statement-breakpoint
CREATE INDEX "anpr_records_status_idx" ON "anpr_records" USING btree ("status");--> statement-breakpoint
CREATE INDEX "anpr_records_captured_at_idx" ON "anpr_records" USING btree ("captured_at");--> statement-breakpoint
CREATE INDEX "anpr_records_camera_idx" ON "anpr_records" USING btree ("camera_id");--> statement-breakpoint
CREATE INDEX "anpr_records_gate_idx" ON "anpr_records" USING btree ("gate_id");--> statement-breakpoint
CREATE INDEX "anpr_records_assigned_ticket_idx" ON "anpr_records" USING btree ("assigned_ticket_id");--> statement-breakpoint
CREATE INDEX "audit_logs_tenant_idx" ON "audit_logs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "audit_logs_entity_idx" ON "audit_logs" USING btree ("entity_type","entity_id");--> statement-breakpoint
CREATE INDEX "audit_logs_action_idx" ON "audit_logs" USING btree ("action");--> statement-breakpoint
CREATE INDEX "audit_logs_timestamp_idx" ON "audit_logs" USING btree ("timestamp");--> statement-breakpoint
CREATE INDEX "audit_logs_user_idx" ON "audit_logs" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "report_templates_tenant_idx" ON "report_templates" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "report_templates_type_idx" ON "report_templates" USING btree ("type");--> statement-breakpoint
CREATE INDEX "report_templates_category_idx" ON "report_templates" USING btree ("category");--> statement-breakpoint
CREATE INDEX "report_templates_active_idx" ON "report_templates" USING btree ("is_active");--> statement-breakpoint
CREATE INDEX "slots_tenant_idx" ON "slots" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "slots_gate_idx" ON "slots" USING btree ("gate_id");--> statement-breakpoint
CREATE INDEX "slots_status_idx" ON "slots" USING btree ("status");--> statement-breakpoint
CREATE INDEX "slots_window_from_idx" ON "slots" USING btree ("window_from");--> statement-breakpoint
CREATE INDEX "slots_assigned_vehicle_idx" ON "slots" USING btree ("assigned_vehicle_id");--> statement-breakpoint
CREATE INDEX "slots_license_plate_idx" ON "slots" USING btree ("license_plate");--> statement-breakpoint
CREATE INDEX "wait_logs_tenant_idx" ON "wait_logs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "wait_logs_ticket_idx" ON "wait_logs" USING btree ("ticket_id");--> statement-breakpoint
CREATE INDEX "wait_logs_gate_idx" ON "wait_logs" USING btree ("gate_id");--> statement-breakpoint
CREATE INDEX "wait_logs_status_idx" ON "wait_logs" USING btree ("status");--> statement-breakpoint
CREATE INDEX "wait_logs_arrival_at_idx" ON "wait_logs" USING btree ("arrival_at");--> statement-breakpoint
CREATE INDEX "wait_logs_license_plate_idx" ON "wait_logs" USING btree ("license_plate");--> statement-breakpoint
CREATE INDEX "wait_logs_slot_idx" ON "wait_logs" USING btree ("slot_id");--> statement-breakpoint
CREATE INDEX "weighing_sessions_tenant_idx" ON "weighing_sessions" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "weighing_sessions_gate_idx" ON "weighing_sessions" USING btree ("gate_id");--> statement-breakpoint
CREATE INDEX "weighing_sessions_scale_idx" ON "weighing_sessions" USING btree ("scale_id");--> statement-breakpoint
CREATE INDEX "weighing_sessions_status_idx" ON "weighing_sessions" USING btree ("status");--> statement-breakpoint
CREATE INDEX "weighing_sessions_started_at_idx" ON "weighing_sessions" USING btree ("started_at");--> statement-breakpoint
CREATE INDEX "weighing_tickets_tenant_idx" ON "weighing_tickets" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "weighing_tickets_status_idx" ON "weighing_tickets" USING btree ("status");--> statement-breakpoint
CREATE INDEX "weighing_tickets_number_idx" ON "weighing_tickets" USING btree ("ticket_number");--> statement-breakpoint
CREATE INDEX "weighing_tickets_license_plate_idx" ON "weighing_tickets" USING btree ("license_plate");--> statement-breakpoint
CREATE INDEX "weighing_tickets_contract_idx" ON "weighing_tickets" USING btree ("contract_id");--> statement-breakpoint
CREATE INDEX "weighing_tickets_order_idx" ON "weighing_tickets" USING btree ("order_id");--> statement-breakpoint
CREATE INDEX "weighing_tickets_gate_idx" ON "weighing_tickets" USING btree ("gate_id");--> statement-breakpoint
CREATE INDEX "weighing_tickets_created_at_idx" ON "weighing_tickets" USING btree ("created_at");