export type McpEventTopic = "agent" | "job" | "task" | "log" | "toast" | "notif" | "workflow";

export interface MCPEventBase {
  id: string;
  ts: string;
  source: "mcp";
  topic: McpEventTopic;
}

export interface AgentEvent extends MCPEventBase {
  topic: "agent";
  status: "starting" | "running" | "idle" | "error" | "done";
  agentId: string;
  message?: string;
}

export interface JobEvent extends MCPEventBase {
  topic: "job";
  jobId: string;
  phase: "queued" | "started" | "progress" | "success" | "failed";
  progress?: number;
  detail?: string;
}

export interface TaskEvent extends MCPEventBase {
  topic: "task";
  taskId: string;
  taskType?: string;
  status: "queued" | "running" | "waiting" | "completed" | "failed";
  detail?: string;
}

export interface LogEvent extends MCPEventBase {
  topic: "log";
  level: "debug" | "info" | "warn" | "error";
  scope?: string;
  text: string;
}

export interface ToastEvent extends MCPEventBase {
  topic: "toast";
  variant: "default" | "destructive" | "success" | "warning" | "info";
  title: string;
  description?: string;
}

export interface NotifEvent extends MCPEventBase {
  topic: "notif";
  title: string;
  body?: string;
  href?: string;
  icon?: string;
}

export interface WorkflowEvent extends MCPEventBase {
  topic: "workflow";
  domain: "sales" | "purchase";
  number: string;
  action: "submit" | "approve" | "reject" | "post";
  fromState: string;
  toState: string;
  user?: string;
}

export type MCPEvent =
  | AgentEvent
  | JobEvent
  | TaskEvent
  | LogEvent
  | ToastEvent
  | NotifEvent
  | WorkflowEvent;

export function isMcpEvent(value: unknown): value is MCPEvent {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const candidate = value as Partial<MCPEvent>;
  if (candidate.source !== "mcp") {
    return false;
  }
  if (typeof candidate.id !== "string" || typeof candidate.ts !== "string") {
    return false;
  }
  if (candidate.topic === "toast") {
    return typeof (candidate as ToastEvent).title === "string";
  }
  if (candidate.topic === "notif") {
    return typeof (candidate as NotifEvent).title === "string";
  }
  if (candidate.topic === "log") {
    return typeof (candidate as LogEvent).text === "string";
  }
  if (candidate.topic === "agent") {
    return typeof (candidate as AgentEvent).agentId === "string";
  }
  if (candidate.topic === "job") {
    return typeof (candidate as JobEvent).jobId === "string";
  }
  if (candidate.topic === "task") {
    return typeof (candidate as TaskEvent).taskId === "string";
  }
  if (candidate.topic === "workflow") {
    const workflowEvent = candidate as WorkflowEvent;
    return typeof workflowEvent.domain === "string" &&
           typeof workflowEvent.number === "string" &&
           typeof workflowEvent.action === "string" &&
           typeof workflowEvent.fromState === "string" &&
           typeof workflowEvent.toState === "string";
  }
  return false;
}
