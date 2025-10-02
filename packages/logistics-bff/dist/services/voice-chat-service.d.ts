export interface VoiceCommand {
    command: string;
    parameters: Record<string, any>;
    confidence: number;
    timestamp: string;
}
export interface ChatMessage {
    id: string;
    userId: string;
    message: string;
    intent?: string;
    entities?: Array<{
        entity: string;
        value: string;
        confidence: number;
    }>;
    response?: string;
    timestamp: string;
}
export declare class VoiceChatService {
    private chatHistory;
    processVoiceCommand(audioData: Buffer, tenantId: string): Promise<VoiceCommand>;
    processChatMessage(message: string, userId: string): Promise<ChatMessage>;
    getChatHistory(userId: string, limit?: number): ChatMessage[];
    private detectIntent;
    private extractEntities;
    private generateResponse;
    private generateId;
}
//# sourceMappingURL=voice-chat-service.d.ts.map