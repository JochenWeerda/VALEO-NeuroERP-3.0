/**
 * Ask VALEO - AI Copilot Dialog
 * Integrated with OpenAI for intelligent assistance
 */

import React, { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Zap, Send, Loader2, Sparkles, X } from 'lucide-react'
import { askVALEO, isOpenAIConfigured, type VALEOMessage } from '@/lib/services/openai-service'

type Message = {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export function AskVALEO() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const location = useLocation()

  // Listen for custom event to open dialog
  useEffect(() => {
    const handleOpen = () => setOpen(true)
    window.addEventListener('open-ask-valeo', handleOpen)
    return () => window.removeEventListener('open-ask-valeo', handleOpen)
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // Build context from current page
      const context = {
        currentPage: location.pathname,
        tenantId: 'demo-tenant', // TODO: Get from auth
      }

      // Convert to OpenAI format
      const conversationHistory: VALEOMessage[] = messages.map((m) => ({
        role: m.role === 'user' ? 'user' : 'assistant',
        content: m.content
      }))

      // Call OpenAI
      const response = await askVALEO(input, context, conversationHistory)

      const assistantMessage: Message = {
        role: 'assistant',
        content: response,
        timestamp: new Date()
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ Fehler: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`,
        timestamp: new Date()
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearConversation = () => {
    setMessages([])
    setInput('')
  }

  // Quick Actions
  const quickActions = [
    'Wie erstelle ich eine Rechnung?',
    'Zeige mir offene Bestellungen',
    'Was ist der Belegfluss?',
    'Compliance-Check für Kunde Schmidt',
  ]

  const isConfigured = isOpenAIConfigured()

  return (
    <>
      {/* Floating Action Button */}
      <Button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-shadow z-50 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        size="icon"
        type="button"
      >
        <Sparkles className="h-6 w-6" />
      </Button>

      {/* Dialog */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary" />
              Ask VALEO
              {!isConfigured && (
                <Badge variant="destructive" className="ml-2">
                  OpenAI nicht konfiguriert
                </Badge>
              )}
            </DialogTitle>
            <DialogDescription>
              Dein intelligenter ERP-Assistent. Frage mich alles über Kunden, Artikel, Prozesse oder Compliance.
            </DialogDescription>
          </DialogHeader>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-4 py-4 min-h-[400px]">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <Sparkles className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-lg font-semibold mb-2">Wie kann ich dir helfen?</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  Stelle mir eine Frage oder wähle eine Schnellaktion:
                </p>
                
                <div className="grid grid-cols-2 gap-2 max-w-lg mx-auto">
                  {quickActions.map((action, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      onClick={() => setInput(action)}
                      className="text-left justify-start h-auto py-3"
                    >
                      {action}
                    </Button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, i) => (
                  <Card key={i} className={msg.role === 'user' ? 'bg-primary/5' : 'bg-muted/50'}>
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0">
                          {msg.role === 'user' ? (
                            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold">
                              DU
                            </div>
                          ) : (
                            <Sparkles className="h-8 w-8 text-primary" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-semibold mb-1">
                            {msg.role === 'user' ? 'Du' : 'VALEO'}
                          </div>
                          <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}

            {loading && (
              <Card className="bg-muted/50">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Loader2 className="h-8 w-8 text-primary animate-spin" />
                    <div className="text-sm text-muted-foreground">
                      VALEO denkt nach...
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Input */}
          <div className="border-t pt-4 space-y-3">
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearConversation}
                className="gap-2"
              >
                <X className="h-4 w-4" />
                Neue Konversation
              </Button>
            )}
            
            <div className="flex gap-2">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={isConfigured ? "Frage VALEO etwas..." : "Bitte OpenAI API-Key konfigurieren"}
                className="min-h-[80px] resize-none"
                disabled={!isConfigured || loading}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || loading || !isConfigured}
                size="icon"
                className="h-[80px] w-[80px]"
              >
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : <Send className="h-6 w-6" />}
              </Button>
            </div>

            {!isConfigured && (
              <p className="text-sm text-muted-foreground">
                💡 Tipp: Setze <code className="bg-muted px-1 py-0.5 rounded">VITE_OPENAI_API_KEY</code> in der <code className="bg-muted px-1 py-0.5 rounded">.env</code> Datei.
              </p>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

