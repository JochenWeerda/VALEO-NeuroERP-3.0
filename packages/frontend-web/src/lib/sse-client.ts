export type SSEOptions = {
  url?: string;
  heartbeatMs?: number;
  retryBaseMs?: number;
  maxRetryMs?: number;
};

type SSEHandlers = {
  onEvent: (eventType: string, event: MessageEvent<string>) => void;
  onOpen?: () => void;
  onError?: (event: Event) => void;
};

const DEFAULT_HEARTBEAT_MS = 25_000;
const DEFAULT_RETRY_BASE_MS = 1_000;
const DEFAULT_MAX_RETRY_MS = 30_000;

function getWindow(): typeof window | undefined {
  if (typeof window === "undefined") {
    return undefined;
  }
  return window;
}

export class SSEClient {
  private es: EventSource | undefined;
  private closed = false;
  private retry = 0;
  private hbTimer: number | undefined;
  private readonly url: string;
  private readonly opts: Required<Omit<SSEOptions, "url">>;
  private readonly handlers: SSEHandlers;
  private readonly registeredTypes = new Set<string>();
  private readonly pendingTypes = new Set<string>(["message"]);
  private readonly boundEventHandler = (event: MessageEvent<string>): void => {
    this.retry = 0;
    const eventType = event.type || "message";
    this.handlers.onEvent(eventType, event);
  };
  private readonly boundOpenHandler = (): void => {
    this.retry = 0;
    this.handlers.onOpen?.();
  };
  private readonly boundErrorHandler = (event: Event): void => {
    this.handlers.onError?.(event);
    this.cleanupES();
    if (this.closed) {
      return;
    }
    this.scheduleReconnect();
  };

  constructor(handlers: SSEHandlers, options: SSEOptions = {}) {
    this.handlers = handlers;
    this.url = options.url ?? "/api/events?stream=mcp";
    this.opts = {
      heartbeatMs: options.heartbeatMs ?? DEFAULT_HEARTBEAT_MS,
      retryBaseMs: options.retryBaseMs ?? DEFAULT_RETRY_BASE_MS,
      maxRetryMs: options.maxRetryMs ?? DEFAULT_MAX_RETRY_MS,
    };
  }

  registerType(type: string): void {
    if (this.registeredTypes.has(type)) {
      return;
    }
    this.pendingTypes.add(type);
    if (this.es) {
      this.es.addEventListener(type, this.boundEventHandler as EventListener);
      this.registeredTypes.add(type);
    }
  }

  start(): void {
    const win = getWindow();
    if (!win) {
      return;
    }
    this.closed = false;
    this.open(win);
  }

  stop(): void {
    this.closed = true;
    this.cleanupES();
    this.retry = 0;
  }

  private open(win: Window & typeof globalThis): void {
    if (this.es) {
      return;
    }
    this.es = new win.EventSource(this.url, { withCredentials: false });
    this.es.addEventListener("open", this.boundOpenHandler as EventListener);
    this.es.addEventListener("error", this.boundErrorHandler as EventListener);
    this.es.onmessage = this.boundEventHandler;

    this.pendingTypes.forEach((type) => {
      if (type === "message") {
        this.es?.addEventListener(type, this.boundEventHandler as EventListener);
      } else {
        this.es?.addEventListener(type, this.boundEventHandler as EventListener);
      }
      this.registeredTypes.add(type);
    });

    const heartbeat = (): void => {
      if (!this.es) {
        return;
      }
      if (this.es.readyState !== win.EventSource.OPEN) {
        this.cleanupES();
        if (!this.closed) {
          this.scheduleReconnect();
        }
      }
    };
    this.hbTimer = win.setInterval(heartbeat, this.opts.heartbeatMs);
  }

  private scheduleReconnect(): void {
    const win = getWindow();
    if (!win) {
      return;
    }
    const delay = Math.min(
      this.opts.retryBaseMs * Math.pow(2, this.retry++),
      this.opts.maxRetryMs,
    );
    win.setTimeout(() => {
      if (this.closed) {
        return;
      }
      this.open(win);
    }, delay);
  }

  private cleanupES(): void {
    if (this.es) {
      try {
        this.es.removeEventListener("open", this.boundOpenHandler as EventListener);
        this.es.removeEventListener("error", this.boundErrorHandler as EventListener);
        this.es.close();
      } catch {
        // ignore
      }
    }
    this.es = undefined;
    const win = getWindow();
    if (win && this.hbTimer !== undefined) {
      win.clearInterval(this.hbTimer);
    }
    this.hbTimer = undefined;
    this.registeredTypes.clear();
  }
}
