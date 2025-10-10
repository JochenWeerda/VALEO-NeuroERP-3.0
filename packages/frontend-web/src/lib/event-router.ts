import { toast } from "@/hooks/use-toast";
import type { MCPEvent, ToastEvent, WorkflowEvent } from "@/lib/mcp-events";

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
      // e.g. notificationStore.add(event)
      break;
    }
    case "log": {
      if (import.meta.env.DEV) {
        const scope = (typeof event.scope === 'string' && event.scope.length > 0) ? `[${event.scope}] ` : "";
        console.info(`${scope}${event.text}`);
      }
      break;
    }
    case "workflow": {
      const workflowEvent = event as WorkflowEvent;
      const actionLabels = {
        submit: "eingereicht",
        approve: "freigegeben",
        reject: "abgelehnt",
        post: "gebucht"
      };
      const domainLabels = {
        sales: "Verkauf",
        purchase: "Einkauf"
      };

      toast({
        title: `Beleg ${actionLabels[workflowEvent.action]}`,
        description: `${domainLabels[workflowEvent.domain]} ${workflowEvent.number}: ${workflowEvent.fromState} → ${workflowEvent.toState}`,
        variant: workflowEvent.action === "reject" ? "destructive" : "default",
      });
      break;
    }
    case "job":
    case "agent":
    case "task":
    default:
      break;
  }
}
