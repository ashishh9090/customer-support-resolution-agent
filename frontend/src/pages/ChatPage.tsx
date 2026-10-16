import React, { useState, useRef, useEffect } from "react";
import type { ChatMessage } from "../types";
import { sendChatMessage } from "../services/api";
import { ExecutionTimeline } from "../components/ExecutionTimeline";
import { StatusBadge } from "../components/StatusBadge";
import {
  Send,
  UtensilsCrossed,
  User,
  Sparkles,
  BookOpen,
  AlertCircle,
  FileCheck2,
  PackageCheck,
  CheckCircle2,
  RefreshCw,
  Bike,
  ShieldCheck,
} from "lucide-react";

interface ChatPageProps {
  initialPrompt?: string;
}

export const ChatPage: React.FC<ChatPageProps> = ({ initialPrompt = "" }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "msg-welcome",
      sender_type: "agent",
      content:
        "Namaste! I am your Zomato Care Resolution Specialist 🛵. I can check live rider & delivery tracking, issue instant meal refunds for orders under $50, submit large orders for manager approval, report spilled/damaged packaging, or answer refund policies. How can I help you today?",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState(initialPrompt);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (initialPrompt) {
      setInput(initialPrompt);
    }
  }, [initialPrompt]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    setError(null);
    setInput("");

    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      sender_type: "customer",
      content: text,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const data = await sendChatMessage(text, conversationId);
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      const agentMsg: ChatMessage = {
        id: `agent-${Date.now()}`,
        sender_type: "agent",
        content: data.response,
        timestamp: new Date().toLocaleTimeString(),
        intent: data.detected_intent,
        confidence: data.confidence,
        citations: data.citations,
        timeline: data.timeline,
        executed_tools: data.executed_tools,
        requires_approval: data.requires_approval,
        approval_id: data.approval_id,
      };

      setMessages((prev) => [...prev, agentMsg]);
    } catch (err: any) {
      setError(err.message || "Failed to process message.");
    } finally {
      setLoading(false);
    }
  };

  const quickChips = [
    { label: "🛵 Where is order ORD-1001?", prompt: "Where is my order ORD-1001? Can you check delivery status?" },
    { label: "⚡ Instant Refund ORD-1001 ($42.50)", prompt: "I want to refund my order ORD-1001." },
    { label: "🛡️ High-Value Refund ORD-1002 ($129.99)", prompt: "I want a full refund for my order ORD-1002." },
    { label: "🍜 Spilled / Damaged Delivery ORD-1001", prompt: "My order ORD-1001 arrived with a broken and shattered case! It is damaged." },
    { label: "💳 Failed Payment on ORD-1006", prompt: "Why was my payment declined on order ORD-1006?" },
    { label: "📜 30-Day Return & Cancellation Policy", prompt: "What is your return and refund policy?" },
  ];

  return (
    <div className="flex flex-col h-full p-6 max-w-5xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2 font-['Outfit']">
            <UtensilsCrossed className="h-5 w-5 text-[#E23744]" />
            Zomato Care Resolution Assistant
          </h2>
          <p className="text-xs text-slate-400">
            LangGraph state machine with verified order database records, instant refund safety, and supervisor approvals.
          </p>
        </div>
        <button
          onClick={() => {
            setMessages([]);
            setConversationId(undefined);
          }}
          className="btn-secondary text-xs"
          id="btn-reset-chat"
        >
          <RefreshCw className="h-3.5 w-3.5 text-[#E23744]" />
          New Chat
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg) => {
          const isCustomer = msg.sender_type === "customer";
          return (
            <div
              key={msg.id}
              className={`flex gap-3 ${isCustomer ? "justify-end" : "justify-start"}`}
            >
              {!isCustomer && (
                <div className="h-8 w-8 rounded-full bg-[#E23744] flex items-center justify-center shrink-0 shadow-md shadow-[#E23744]/30">
                  <UtensilsCrossed className="h-4 w-4 text-white" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                  isCustomer
                    ? "bg-gradient-to-r from-[#E23744] to-[#B81F2D] text-white rounded-br-none shadow-md shadow-[#E23744]/25"
                    : "glass-panel text-slate-200 rounded-bl-none border border-slate-700/60"
                }`}
              >
                {/* Meta details for agent turn */}
                {!isCustomer && msg.intent && (
                  <div className="flex flex-wrap items-center gap-2 pb-1.5 border-b border-slate-700/40 text-[10px] text-slate-400">
                    <span>
                      Intent: <strong className="text-[#FF6B77] font-mono">{msg.intent}</strong>
                    </span>
                    {msg.confidence !== undefined && (
                      <span>
                        Confidence: <strong className="text-emerald-400">{(msg.confidence * 100).toFixed(0)}%</strong>
                      </span>
                    )}
                    {msg.requires_approval && (
                      <span className="rounded bg-amber-500/20 px-1.5 py-0.5 text-amber-300 font-bold border border-amber-500/30">
                        Reviewer Approval Required
                      </span>
                    )}
                  </div>
                )}

                {/* Content */}
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Citations */}
                {!isCustomer && msg.citations && msg.citations.length > 0 && (
                  <div className="pt-2 border-t border-slate-700/40 space-y-1">
                    <p className="text-[10px] font-bold text-[#F4A261] flex items-center gap-1 font-['Outfit']">
                      <BookOpen className="h-3 w-3 text-[#E23744]" /> Grounded Policy Citations:
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.citations.map((c, idx) => (
                        <span
                          key={idx}
                          className="rounded-lg bg-[#E23744]/15 border border-[#E23744]/30 px-2 py-0.5 text-[10px] text-[#FF9EAA] font-mono"
                        >
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Execution Timeline Stepper */}
                {!isCustomer && msg.timeline && msg.timeline.length > 0 && (
                  <ExecutionTimeline timeline={msg.timeline} executedTools={msg.executed_tools} />
                )}

                <div className="text-[9px] text-right opacity-60">{msg.timestamp}</div>
              </div>

              {isCustomer && (
                <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0">
                  <User className="h-4 w-4 text-slate-300" />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="h-8 w-8 rounded-full bg-[#E23744] flex items-center justify-center shrink-0 shadow-md shadow-[#E23744]/30">
              <UtensilsCrossed className="h-4 w-4 text-white" />
            </div>
            <div className="glass-panel p-4 text-xs text-slate-300 rounded-2xl rounded-bl-none flex items-center gap-2 border border-[#E23744]/30">
              <Sparkles className="h-4 w-4 text-[#E23744] animate-spin" />
              <span>Verifying order records, consulting Zomato policies & tools...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-3 text-xs text-rose-300 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Chips */}
      <div className="flex flex-wrap gap-2 pt-1">
        {quickChips.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip.prompt)}
            className="rounded-full bg-slate-800/80 hover:bg-[#E23744]/20 hover:text-[#FF6B77] hover:border-[#E23744]/40 border border-slate-700/60 px-3 py-1.5 text-[11px] text-slate-300 transition-all font-medium"
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex gap-2"
      >
        <input
          id="chat-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Zomato Care about order status, refunds, spilled packaging, or policies..."
          disabled={loading}
          className="flex-1 rounded-xl border border-slate-700 bg-slate-900/90 px-4 py-3 text-xs text-white placeholder-slate-500 focus:border-[#E23744] focus:outline-none focus:ring-1 focus:ring-[#E23744]/40"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          id="btn-send-message"
          className="btn-primary"
        >
          <Send className="h-4 w-4" />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
};
