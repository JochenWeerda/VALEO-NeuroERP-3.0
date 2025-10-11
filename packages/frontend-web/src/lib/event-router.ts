import { toast } from "@/hooks/use-toast";
import type { MCPEvent, ToastEvent } from "@/lib/mcp-events";

function mapVariant(variant: ToastEvent["variant"]): "default" | "destructive" {
  return variant === "destructive" ? "destructive" : "default";
}

export function routeMCPEvent(event: MCPEvent): void {
  switch (event.topic) {
    case "toast": {
      toast({
        title: event.title,
        description: event.description,
        variant: mapVariant(event.variant),
      });
      break;
    }
    case "notif": {
      // Placeholder for future notification center integration
      break;
    }
    case "log": {
      if (import.meta.env.DEV) {
        const scope =
          typeof event.scope === "string" && event.scope.length > 0 ? `[${event.scope}] ` : "";
        console.info(`${scope}${event.text}`);
      }
      break;
    }
    case "workflow": {
      const actionLabels: Record<string, string> = {
        submit: "eingereicht",
        approve: "freigegeben",
        reject: "abgelehnt",
        post: "gebucht",
      };
      const domainLabels: Record<string, string> = {
        sales: "Verkauf",
        purchase: "Einkauf",
      };

      toast({
        title: `Beleg ${actionLabels[event.action] ?? event.action}`,
        description: `${domainLabels[event.domain] ?? event.domain} ${event.number}: ${event.fromState} -> ${event.toState}`,
        variant: event.action === "reject" ? "destructive" : "default",
      });
      break;
    }
    default:
      break;
  }
}
