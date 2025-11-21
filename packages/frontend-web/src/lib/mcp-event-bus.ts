import { SSEClient, type SSEOptions } from "@/lib/sse-client";
import { type MCPEvent, isMcpEvent } from "@/lib/mcp-events";

export type ConnectionState = "idle" | "connecting" | "open" | "error";

export type McpRealtimeEvent = {
  service: string;
  type: string;
  rawType: string;
  payload: unknown;
  timestamp: number;
};

export type McpRealtimeListener = (_event: McpRealtimeEvent) => void;
export type McpTypedListener = (_event: MCPEvent) => void;
export type ConnectionListener = (_state: ConnectionState) => void;

const ALL_SERVICES_TOKEN = "*";

const SERVICE_EVENT_TYPE_MAP: Record<string, string[]> = {
  inventory: ["inventory", "inventory.created", "inventory.updated", "inventory.adjusted", "inventory.moved"],
  weighing: ["weighing", "weighing.created", "weighing.updated", "weighing.finalized"],
  pipeline_status: ["pipeline_status"],
  handover: ["handover"],
  cursor_prompt: ["cursor_prompt"],
  heartbeat: ["heartbeat"],
};

function parsePayload(raw: unknown): unknown {
  if (typeof raw !== "string") {
    return raw;
  }
  const trimmed = raw.trim();
  if (trimmed.length === 0) {
    return undefined;
  }
  try {
    return JSON.parse(trimmed);
  } catch {
    return trimmed;
  }
}

function normalizeEvent(rawType: string, payload: unknown): McpRealtimeEvent {
  let candidateType = rawType;
  if (typeof payload === "object" && payload !== null) {
    const maybeType = (payload as Record<string, unknown>).eventType;
    if (typeof maybeType === "string" && maybeType.length > 0) {
      candidateType = maybeType;
    }
  }

  const resolvedRawType = candidateType.length > 0 ? candidateType : rawType || "message";

  let service = "";
  if (typeof payload === "object" && payload !== null) {
    const maybeService = (payload as Record<string, unknown>).service;
    if (typeof maybeService === "string" && maybeService.length > 0) {
      service = maybeService;
    }
  }

  if (service.length === 0 && resolvedRawType.includes(".")) {
    service = resolvedRawType.substring(0, resolvedRawType.indexOf("."));
  }
  if (service.length === 0) {
    service = resolvedRawType !== "message" ? resolvedRawType : "general";
  }

  const normalizedType = resolvedRawType.includes(".")
    ? resolvedRawType.substring(resolvedRawType.lastIndexOf(".") + 1)
    : resolvedRawType;

  return {
    service,
    type: normalizedType,
    rawType: resolvedRawType,
    payload,
    timestamp: Date.now(),
  };
}

function hasAnyListeners<T>(registry: Map<string, Set<T>>): boolean {
  for (const set of registry.values()) {
    if (set.size > 0) {
      return true;
    }
  }
  return false;
}

class McpEventBus {
  private client: SSEClient | undefined;
  private readonly typedListeners = new Set<McpTypedListener>();
  private readonly serviceListeners = new Map<string, Set<McpRealtimeListener>>();
  private readonly stateListeners = new Set<ConnectionListener>();
  private connectionState: ConnectionState = "idle";
  private readonly registeredTypes = new Set<string>();
  private eventsUrl: string | undefined =
    typeof import.meta !== "undefined" && typeof import.meta.env?.VITE_MCP_EVENTS_URL === "string"
      ? import.meta.env.VITE_MCP_EVENTS_URL
      : undefined;
  private sseOptions: SSEOptions = {};

  addConnectionListener(listener: ConnectionListener): () => void {
    this.stateListeners.add(listener);
    listener(this.connectionState);
    return () => {
      this.stateListeners.delete(listener);
    };
  }

  addTypedListener(listener: McpTypedListener): () => void {
    this.typedListeners.add(listener);
    this.ensureClient();
    return () => {
      this.typedListeners.delete(listener);
      this.evaluateShutdown();
    };
  }

  addServiceListener(service: string, listener: McpRealtimeListener): () => void {
    const key = service.length > 0 ? service : ALL_SERVICES_TOKEN;
    let listeners = this.serviceListeners.get(key);
    if (!listeners) {
      listeners = new Set();
      this.serviceListeners.set(key, listeners);
    }
    listeners.add(listener);
    this.ensureClient();
    this.registerServiceTypes(key);

    return () => {
      const current = this.serviceListeners.get(key);
      if (!current) {
        return;
      }
      current.delete(listener);
      if (current.size === 0) {
        this.serviceListeners.delete(key);
      }
      this.evaluateShutdown();
    };
  }

  setEventsUrl(url: string | undefined): void {
    if (url === this.eventsUrl) {
      return;
    }
    this.eventsUrl = url;
    this.applyOptions({ url });
  }

  setAuthTokenResolver(resolver?: () => string | undefined): void {
    this.applyOptions({ getToken: resolver });
  }

  setWithCredentials(enabled: boolean): void {
    this.applyOptions({ withCredentials: enabled });
  }

  getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  private ensureClient(): void {
    if (typeof window === "undefined") {
      return;
    }
    if (this.client) {
      return;
    }
    if (!this.shouldRun()) {
      return;
    }
    const options: SSEOptions = {
      ...this.sseOptions,
    };
    if ((typeof options.url !== "string" || options.url.length === 0) && typeof this.eventsUrl === "string" && this.eventsUrl.length > 0) {
      options.url = this.eventsUrl;
    }
    this.client = new SSEClient(
      {
        onEvent: (_eventType, _event) => this.handleEvent(_eventType, _event),
        onOpen: () => this.transition("open"),
        onError: (): void => {
          this.transition("error");
          this.transition("connecting");
        },
      },
      options,
    );
    // ensure default type is tracked
    this.client.registerType("message");
    for (const type of this.registeredTypes.values()) {
      this.client.registerType(type);
    }
    this.transition("connecting");
    this.client.start();
  }

  private applyOptions(partial: SSEOptions): void {
    this.sseOptions = { ...this.sseOptions, ...partial };
    if (this.client) {
      this.client.stop();
      this.client = undefined;
      this.transition("idle");
    }
    if (this.shouldRun()) {
      this.ensureClient();
    }
  }

  private registerServiceTypes(service: string): void {
    if (service === ALL_SERVICES_TOKEN) {
      Object.values(SERVICE_EVENT_TYPE_MAP).forEach((types) => {
        types.forEach((type) => this.registerEventType(type));
      });
      this.registerEventType("message");
      this.registerEventType("heartbeat");
      return;
    }
    const mapped = SERVICE_EVENT_TYPE_MAP[service];
    if (mapped !== undefined) {
      mapped.forEach((type) => this.registerEventType(type));
    } else {
      this.registerEventType(service);
    }
  }

  private registerEventType(type: string): void {
    if (this.registeredTypes.has(type)) {
      return;
    }
    this.registeredTypes.add(type);
    if (this.client) {
      this.client.registerType(type);
    }
  }

  private dispatchServiceEvent(event: McpRealtimeEvent): void {
    const listeners = this.serviceListeners.get(event.service);
    listeners?.forEach((listener) => listener(event));

    const wildcard = this.serviceListeners.get(ALL_SERVICES_TOKEN);
    wildcard?.forEach((listener) => listener(event));
  }

  private handleEvent(_eventType: string, event: MessageEvent<string>): void {
    if (this.connectionState !== "open") {
      this.transition("open");
    }
    const parsed = parsePayload(event.data);

    if (isMcpEvent(parsed)) {
      this.typedListeners.forEach((listener) => listener(parsed));
    }

    const normalized = normalizeEvent(_eventType, parsed);
    this.dispatchServiceEvent(normalized);
  }

  private shouldRun(): boolean {
    return this.typedListeners.size > 0 || hasAnyListeners(this.serviceListeners) || this.stateListeners.size > 0;
  }

  private evaluateShutdown(): void {
    if (this.shouldRun()) {
      return;
    }
    if (this.client) {
      this.client.stop();
      this.client = undefined;
    }
    this.transition("idle");
  }

  private transition(state: ConnectionState): void {
    if (this.connectionState === state) {
      return;
    }
    this.connectionState = state;
    this.stateListeners.forEach((listener) => listener(state));
  }
}

export const mcpEventBus = new McpEventBus();

