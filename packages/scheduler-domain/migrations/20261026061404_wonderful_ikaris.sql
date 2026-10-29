CREATE TABLE "calendars" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"tenant_id" text,
	"key" text NOT NULL,
	"name" text NOT NULL,
	"holidays" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"business_days" jsonb DEFAULT '{"mon":true,"tue":true,"wed":true,"thu":true,"fri":true,"sat":false,"sun":false}'::jsonb NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "jobs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"tenant_id" text NOT NULL,
	"key" text NOT NULL,
	"queue" text DEFAULT 'default' NOT NULL,
	"priority" integer DEFAULT 5 NOT NULL,
	"max_attempts" integer DEFAULT 3 NOT NULL,
	"backoff_strategy" text DEFAULT 'EXPONENTIAL' NOT NULL,
	"backoff_base_sec" integer DEFAULT 60 NOT NULL,
	"backoff_max_sec" integer,
	"timeout_sec" integer DEFAULT 300 NOT NULL,
	"concurrency_limit" integer,
	"sla_sec" integer,
	"enabled" boolean DEFAULT true NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "runs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"tenant_id" text NOT NULL,
	"schedule_id" uuid,
	"job_id" uuid,
	"dedupe_key" text,
	"status" text DEFAULT 'Pending' NOT NULL,
	"started_at" timestamp with time zone,
	"finished_at" timestamp with time zone,
	"attempt" integer DEFAULT 1 NOT NULL,
	"error" text,
	"latency_ms" integer,
	"duration_ms" integer,
	"worker_id" uuid,
	"payload" jsonb
);
--> statement-breakpoint
CREATE TABLE "schedules" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"tenant_id" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"tz" text DEFAULT 'Europe/Berlin' NOT NULL,
	"trigger_type" text NOT NULL,
	"trigger_config" jsonb NOT NULL,
	"target_type" text NOT NULL,
	"target_config" jsonb NOT NULL,
	"payload" jsonb,
	"calendar_config" jsonb,
	"enabled" boolean DEFAULT true NOT NULL,
	"next_fire_at" timestamp with time zone,
	"last_fire_at" timestamp with time zone,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "workers" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"tenant_id" text,
	"name" text NOT NULL,
	"capabilities" jsonb NOT NULL,
	"heartbeat_at" timestamp with time zone DEFAULT now() NOT NULL,
	"status" text DEFAULT 'Online' NOT NULL,
	"max_parallel" integer DEFAULT 10 NOT NULL,
	"current_jobs" integer DEFAULT 0 NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
ALTER TABLE "runs" ADD CONSTRAINT "runs_schedule_id_schedules_id_fk" FOREIGN KEY ("schedule_id") REFERENCES "public"."schedules"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "runs" ADD CONSTRAINT "runs_job_id_jobs_id_fk" FOREIGN KEY ("job_id") REFERENCES "public"."jobs"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "runs" ADD CONSTRAINT "runs_worker_id_workers_id_fk" FOREIGN KEY ("worker_id") REFERENCES "public"."workers"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "calendars_tenant_idx" ON "calendars" USING btree ("tenant_id");--> statement-breakpoint
CREATE UNIQUE INDEX "calendars_key_idx" ON "calendars" USING btree ("key");--> statement-breakpoint
CREATE INDEX "jobs_tenant_idx" ON "jobs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "jobs_queue_idx" ON "jobs" USING btree ("queue");--> statement-breakpoint
CREATE INDEX "jobs_enabled_idx" ON "jobs" USING btree ("enabled");--> statement-breakpoint
CREATE UNIQUE INDEX "jobs_tenant_key_idx" ON "jobs" USING btree ("tenant_id","key");--> statement-breakpoint
CREATE INDEX "runs_tenant_idx" ON "runs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "runs_schedule_idx" ON "runs" USING btree ("schedule_id");--> statement-breakpoint
CREATE INDEX "runs_job_idx" ON "runs" USING btree ("job_id");--> statement-breakpoint
CREATE INDEX "runs_status_idx" ON "runs" USING btree ("status");--> statement-breakpoint
CREATE INDEX "runs_worker_idx" ON "runs" USING btree ("worker_id");--> statement-breakpoint
CREATE INDEX "runs_started_idx" ON "runs" USING btree ("started_at");--> statement-breakpoint
CREATE UNIQUE INDEX "runs_dedupe_idx" ON "runs" USING btree ("dedupe_key");--> statement-breakpoint
CREATE INDEX "schedule_runs_idx" ON "runs" USING btree ("schedule_id","status");--> statement-breakpoint
CREATE INDEX "job_runs_idx" ON "runs" USING btree ("job_id","status");--> statement-breakpoint
CREATE INDEX "runs_tenant_time_idx" ON "runs" USING btree ("tenant_id","created_at");--> statement-breakpoint
CREATE INDEX "schedules_tenant_idx" ON "schedules" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "schedules_enabled_idx" ON "schedules" USING btree ("enabled");--> statement-breakpoint
CREATE INDEX "schedules_next_fire_idx" ON "schedules" USING btree ("next_fire_at");--> statement-breakpoint
CREATE UNIQUE INDEX "schedules_tenant_name_idx" ON "schedules" USING btree ("tenant_id","name");--> statement-breakpoint
CREATE INDEX "workers_tenant_idx" ON "workers" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "workers_status_idx" ON "workers" USING btree ("status");--> statement-breakpoint
CREATE INDEX "workers_heartbeat_idx" ON "workers" USING btree ("heartbeat_at");--> statement-breakpoint
CREATE UNIQUE INDEX "workers_name_idx" ON "workers" USING btree ("name");