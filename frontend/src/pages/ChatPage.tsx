import React, { useState, useRef, useEffect } from "react";
import type { ChatMessage } from "../types";
import { sendChatMessage } from "../services/api";
import { ExecutionTimeline } from "../components/ExecutionTimeline";
import { StatusBadge } from "../components/StatusBadge";
import {
  Send,
  Bot,
  User,
  Sparkles,
  BookOpen,
  AlertCircle,
  FileCheck2,
  PackageCheck,
  CheckCircle2,
  RefreshCw,
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
        "Hello! I am your AI Customer Support Assistant. I can check order status, process eligible refunds in sandbox mode, open damaged item tickets, investigate payment errors, or answer policy questions. How can I help you today?",
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
    "Where is my order ORD-1001?",
    "Refund my order ORD-1001",
    "Refund high-value smartwatch ORD-1002",
    "Order ORD-1001 arrived damaged with broken parts",
    "Why was payment declined on ORD-1006?",
    "What is your 30-day return policy?",
  ];

  return (
    <div className="flex flex-col h-full p-6 max-w-5xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bot className="h-5 w-5 text-indigo-400" />
            AI Customer Support Resolution Assistant
          </h2>
          <p className="text-xs text-slate-400">
            Real LangGraph state machine with verified tool execution and human escalation.
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
          <RefreshCw className="h-3.5 w-3.5" />
          New Conversation
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
                <div className="h-8 w-8 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4 text-indigo-400" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                  isCustomer
                    ? "bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-600/20"
                    : "glass-panel text-slate-200 rounded-bl-none"
                }`}
              >
                {/* Meta details for agent turn */}
                {!isCustomer && msg.intent && (
                  <div className="flex flex-wrap items-center gap-2 pb-1 border-b border-slate-700/40 text-[10px] text-slate-400">
                    <span>
                      Intent: <strong className="text-indigo-300 font-mono">{msg.intent}</strong>
                    </span>
                    {msg.confidence !== undefined && (
                      <span>
                        Confidence: <strong className="text-emerald-400">{(msg.confidence * 100).toFixed(0)}%</strong>
                      </span>
                    )}
                    {msg.requires_approval && (
                      <span className="rounded bg-amber-500/20 px-1.5 py-0.5 text-amber-300 font-semibold border border-amber-500/30">
                        Approval Required
                      </span>
                    )}
                  </div>
                )}

                {/* Content */}
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Citations */}
                {!isCustomer && msg.citations && msg.citations.length > 0 && (
                  <div className="pt-2 border-t border-slate-700/40 space-y-1">
                    <p className="text-[10px] font-semibold text-cyan-400 flex items-center gap-1">
                      <BookOpen className="h-3 w-3" /> Grounded Policy Citations:
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.citations.map((c, idx) => (
                        <span
                          key={idx}
                          className="rounded bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 text-[10px] text-cyan-200 font-mono"
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
            <div className="h-8 w-8 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center shrink-0">
              <Bot className="h-4 w-4 text-indigo-400" />
            </div>
            <div className="glass-panel p-4 text-xs text-slate-300 rounded-2xl rounded-bl-none flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-indigo-400 animate-spin" />
              <span>Orchestrating workflow, checking policies & tools...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-rose-500/30 bg-rose-950/30 p-3 text-xs text-rose-300 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompts */}
      <div className="flex flex-wrap gap-1.5 pt-1">
        {quickChips.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip)}
            className="rounded-full border border-slate-700/60 bg-slate-800/40 px-2.5 py-1 text-[11px] text-slate-300 hover:border-indigo-500 hover:bg-slate-700/60 transition-colors"
          >
            {chip}
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
          placeholder="Type an issue, order inquiry (e.g. ORD-1001), or policy question..."
          className="flex-1 rounded-xl border border-slate-700 bg-slate-900/90 px-4 py-3 text-xs text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
        />
        <button
          id="chat-submit-btn"
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary px-5 disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
};
