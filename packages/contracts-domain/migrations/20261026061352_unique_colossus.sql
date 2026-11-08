CREATE TABLE "amendments" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"contract_id" uuid NOT NULL,
	"tenant_id" uuid NOT NULL,
	"type" text NOT NULL,
	"reason" text NOT NULL,
	"changes" jsonb NOT NULL,
	"approved_by" uuid,
	"approved_at" timestamp with time zone,
	"status" text DEFAULT 'Pending' NOT NULL,
	"effective_at" timestamp with time zone,
	"notes" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "call_offs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"contract_id" uuid NOT NULL,
	"tenant_id" uuid NOT NULL,
	"qty" numeric(15, 3) NOT NULL,
	"window_from" timestamp with time zone NOT NULL,
	"window_to" timestamp with time zone NOT NULL,
	"site" text,
	"silo" text,
	"customer_yard" text,
	"status" text DEFAULT 'Planned' NOT NULL,
	"notes" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "contracts" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid NOT NULL,
	"contract_no" text NOT NULL,
	"type" text NOT NULL,
	"commodity" text NOT NULL,
	"counterparty_id" uuid NOT NULL,
	"incoterm" text,
	"delivery_window_from" timestamp with time zone NOT NULL,
	"delivery_window_to" timestamp with time zone NOT NULL,
	"qty_unit" text NOT NULL,
	"qty_contracted" numeric(15, 3) NOT NULL,
	"qty_tolerance" numeric(5, 2),
	"pricing_mode" text NOT NULL,
	"pricing_reference_market" text,
	"pricing_futures_month" text,
	"pricing_basis" numeric(10, 2),
	"pricing_fees" jsonb,
	"pricing_fx" jsonb,
	"pricing_last_fixing_at" timestamp with time zone,
	"delivery_shipment_type" text NOT NULL,
	"delivery_parity" text,
	"delivery_storage" jsonb,
	"delivery_quality_specs" jsonb,
	"status" text DEFAULT 'Draft' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"version" integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fulfilments" (
	"contract_id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"delivered_qty" numeric(15, 3) DEFAULT '0' NOT NULL,
	"priced_qty" numeric(15, 3) DEFAULT '0' NOT NULL,
	"invoiced_qty" numeric(15, 3) DEFAULT '0' NOT NULL,
	"open_qty" numeric(15, 3) NOT NULL,
	"avg_price" numeric(10, 2),
	"timeline" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"last_updated" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "hedge_refs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"contract_id" uuid NOT NULL,
	"tenant_id" uuid NOT NULL,
	"instrument" text NOT NULL,
	"market" text NOT NULL,
	"symbol" text NOT NULL,
	"month" text NOT NULL,
	"qty" numeric(15, 3) NOT NULL,
	"side" text NOT NULL,
	"link_id" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "amendments" ADD CONSTRAINT "amendments_contract_id_contracts_id_fk" FOREIGN KEY ("contract_id") REFERENCES "public"."contracts"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "call_offs" ADD CONSTRAINT "call_offs_contract_id_contracts_id_fk" FOREIGN KEY ("contract_id") REFERENCES "public"."contracts"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "fulfilments" ADD CONSTRAINT "fulfilments_contract_id_contracts_id_fk" FOREIGN KEY ("contract_id") REFERENCES "public"."contracts"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "hedge_refs" ADD CONSTRAINT "hedge_refs_contract_id_contracts_id_fk" FOREIGN KEY ("contract_id") REFERENCES "public"."contracts"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "amendments_contract_id_idx" ON "amendments" USING btree ("contract_id");--> statement-breakpoint
CREATE INDEX "amendments_tenant_id_idx" ON "amendments" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "amendments_status_idx" ON "amendments" USING btree ("status");--> statement-breakpoint
CREATE INDEX "call_offs_contract_id_idx" ON "call_offs" USING btree ("contract_id");--> statement-breakpoint
CREATE INDEX "call_offs_tenant_id_idx" ON "call_offs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "call_offs_status_idx" ON "call_offs" USING btree ("status");--> statement-breakpoint
CREATE INDEX "call_offs_window_idx" ON "call_offs" USING btree ("window_from","window_to");--> statement-breakpoint
CREATE INDEX "contracts_tenant_id_idx" ON "contracts" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "contracts_counterparty_id_idx" ON "contracts" USING btree ("counterparty_id");--> statement-breakpoint
CREATE INDEX "contracts_status_idx" ON "contracts" USING btree ("status");--> statement-breakpoint
CREATE INDEX "contracts_commodity_idx" ON "contracts" USING btree ("commodity");--> statement-breakpoint
CREATE INDEX "contracts_type_idx" ON "contracts" USING btree ("type");--> statement-breakpoint
CREATE INDEX "contracts_delivery_window_idx" ON "contracts" USING btree ("delivery_window_from","delivery_window_to");--> statement-breakpoint
CREATE INDEX "fulfilments_tenant_id_idx" ON "fulfilments" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "hedge_refs_contract_id_idx" ON "hedge_refs" USING btree ("contract_id");--> statement-breakpoint
CREATE INDEX "hedge_refs_tenant_id_idx" ON "hedge_refs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "hedge_refs_link_id_idx" ON "hedge_refs" USING btree ("link_id");