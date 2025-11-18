"use client";

import { useState, useRef, useEffect } from "react";
import { Card } from "@/components/ui/card";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  agentLogs?: string[];
}

interface ChatInterfaceProps {
  onAnalyze: (adUrl: string | File, lpUrl: string, guidelines?: string) => void;
  messages: Message[];
  isAnalyzing: boolean;
}

export default function ChatInterface({
  onAnalyze,
  messages,
  isAnalyzing,
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-280px)]">
      {/* Messages Container */}
      <Card className="flex-1 overflow-hidden flex flex-col border-gray-200 shadow-sm">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center mb-6">
                <span className="text-3xl">🎯</span>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Bereit für die Analyse
              </h2>
              <p className="text-gray-600 max-w-lg mb-8 text-sm leading-relaxed">
                Lade dein Ad-Motiv hoch und gib die Landingpage-URL ein, um eine detaillierte Qualitätsanalyse zu erhalten.
              </p>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 max-w-md text-left">
                <p className="font-medium text-gray-900 mb-3 text-sm">Benötigte Informationen:</p>
                <ul className="space-y-2 text-gray-700 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">•</span>
                    <span>Ad-Motiv (Datei oder URL)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">•</span>
                    <span>Landingpage URL</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">•</span>
                    <span>Optional: Zielgruppe, Kampagnenziel & Brand Guidelines</span>
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-5 bg-white">
          <ChatInput onSubmit={onAnalyze} isAnalyzing={isAnalyzing} />
        </div>
      </Card>
    </div>
  );
}
