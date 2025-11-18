"use client";

import { Message } from "./ChatInterface";
import AgentThinking from "./AgentThinking";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  // If it's a loading message with agent logs, show AgentThinking component
  if (message.isLoading && message.agentLogs && message.agentLogs.length > 0) {
    return (
      <div className="flex justify-start">
        <AgentThinking logs={message.agentLogs} />
      </div>
    );
  }

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} ${
        isSystem ? "justify-center" : ""
      }`}
    >
      <div
        className={`max-w-[85%] ${
          isUser
            ? "bg-primary text-white rounded-2xl rounded-tr-sm"
            : isSystem
            ? "bg-gray-100 text-gray-600 rounded-lg text-sm italic"
            : "bg-white border border-gray-200 rounded-2xl rounded-tl-sm shadow-sm"
        } ${isSystem ? "px-4 py-2" : "p-4"}`}
      >
        {/* Message Header */}
        {!isSystem && (
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">
              {isUser ? "👤" : "🤖"}
            </span>
            <span className={`text-xs font-medium ${isUser ? "text-white/80" : "text-gray-500"}`}>
              {isUser ? "Du" : "AI Analyst"}
            </span>
            <span className={`text-xs ${isUser ? "text-white/60" : "text-gray-400"}`}>
              {message.timestamp.toLocaleTimeString("de-DE", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>
        )}

        {/* Message Content */}
        <div className={isUser ? "text-white" : "text-gray-700"}>
          {message.isLoading ? (
            <div className="flex items-center gap-2">
              <span className="animate-pulse">Analysiere deine Ads</span>
              <span className="flex gap-1">
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
              </span>
            </div>
          ) : !isUser && !isSystem ? (
            <div className="prose prose-sm max-w-none prose-headings:text-gray-800 prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:text-gray-700 prose-li:text-gray-700">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="whitespace-pre-wrap">{message.content}</p>
          )}
        </div>
      </div>
    </div>
  );
}
