"use client";

import { useState } from "react";
import ChatInterface, { Message } from "@/components/ChatInterface";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async (
    adInput: string | File,
    lpUrl: string,
    targetAudience?: string,
    campaignGoal?: string,
    guidelines?: string
  ) => {
    const isFile = adInput instanceof File;

    // Build user message content
    let content = isFile
      ? `📤 Ad-Datei: ${adInput.name}\n📄 LP-URL: ${lpUrl}`
      : `📎 Ad-URL: ${adInput}\n📄 LP-URL: ${lpUrl}`;

    if (targetAudience) content += `\n🎯 Zielgruppe: ${targetAudience}`;
    if (campaignGoal) content += `\n🎁 Kampagnenziel: ${campaignGoal}`;
    if (guidelines) content += '\n📋 Brand Guidelines: Ja';

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    // Add loading message
    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "Analysiere...",
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages(prev => [...prev, loadingMessage]);
    setIsAnalyzing(true);

    // Track logs for the loading message
    const agentLogs: string[] = [];
    const loadingMessageId = loadingMessage.id;

    try {
      // Use streaming endpoint with FormData
      const formData = new FormData();
      formData.append("landing_page_url", lpUrl);

      if (isFile) {
        formData.append("ad_file", adInput);
      } else {
        formData.append("ad_url", adInput);
      }

      if (targetAudience) {
        formData.append("target_audience", targetAudience);
      }

      if (campaignGoal) {
        formData.append("campaign_goal", campaignGoal);
      }

      if (guidelines) {
        formData.append("brand_guidelines", guidelines);
      }

      const response = await fetch("http://localhost:8000/api/v1/analyze/stream", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      let resultText: string | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === "result") {
                resultText = data.data;
              } else if (data.type === "error") {
                throw new Error(data.data);
              } else if (data.type === "log") {
                // Add log to array and update loading message
                agentLogs.push(data.data);
                setMessages(prev =>
                  prev.map(m =>
                    m.id === loadingMessageId
                      ? { ...m, agentLogs: [...agentLogs] }
                      : m
                  )
                );
              }
              // Ignore heartbeats
            } catch (parseError) {
              console.warn("Failed to parse SSE data:", line);
            }
          }
        }
      }

      if (!resultText) {
        throw new Error("No result received");
      }

      // Remove loading message and add result as markdown content
      setMessages(prev => {
        const withoutLoading = prev.filter(m => !m.isLoading);
        return [
          ...withoutLoading,
          {
            id: Date.now().toString(),
            role: "assistant",
            content: resultText,
            timestamp: new Date(),
          },
        ];
      });
    } catch (error) {
      console.error("Analysis error:", error);

      // Remove loading and add error message
      setMessages(prev => {
        const withoutLoading = prev.filter(m => !m.isLoading);
        return [
          ...withoutLoading,
          {
            id: Date.now().toString(),
            role: "assistant",
            content: `❌ Fehler bei der Analyse: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`,
            timestamp: new Date(),
          },
        ];
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="container mx-auto px-4 py-12 max-w-6xl">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-xl">🎯</span>
            </div>
            <div>
              <h1 className="text-3xl font-semibold text-gray-900">
                Ads Quality Rater
              </h1>
              <p className="text-sm text-gray-500 mt-0.5">
                KI-basierte Bewertung von Ad-LP-Kohärenz und Markenkonformität
              </p>
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <ChatInterface
          messages={messages}
          onAnalyze={handleAnalyze}
          isAnalyzing={isAnalyzing}
        />

        {/* Footer */}
        <footer className="mt-12 text-center text-xs text-gray-500 border-t border-gray-200 pt-6">
          <p>
            Powered by Gemini 2.0 Flash & Crew AI
          </p>
          <p className="mt-1 text-gray-400">© 2025 flin. All rights reserved.</p>
        </footer>
      </div>
    </main>
  );
}
