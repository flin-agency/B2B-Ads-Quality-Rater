"use client";

import { useState, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
  onSubmit: (
    adUrl: string | File,
    lpUrl: string,
    targetAudience?: string,
    campaignGoal?: string,
    guidelines?: string
  ) => void;
  isAnalyzing: boolean;
}

export default function ChatInput({ onSubmit, isAnalyzing }: ChatInputProps) {
  const [adFile, setAdFile] = useState<File | null>(null);
  const [lpUrl, setLpUrl] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [campaignGoal, setCampaignGoal] = useState("");
  const [guidelines, setGuidelines] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (adFile && lpUrl.trim()) {
      onSubmit(
        adFile,
        lpUrl,
        targetAudience || undefined,
        campaignGoal || undefined,
        guidelines || undefined
      );
      setAdFile(null);
      setLpUrl("");
      setTargetAudience("");
      setCampaignGoal("");
      setGuidelines("");
      setShowAdvanced(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setAdFile(file);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Ad-Motiv (Bild hochladen)
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={isAnalyzing}
              required
              className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary file:text-white hover:file:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            />
            {adFile && (
              <div className="text-xs text-gray-600 flex items-center gap-2 bg-slate-50 px-3 py-2 rounded-md">
                <span className="text-accent">✓</span>
                <span>{adFile.name} ({(adFile.size / 1024).toFixed(0)} KB)</span>
              </div>
            )}
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Landing Page URL
            </label>
            <Input
              type="url"
              placeholder="https://example.com/landing-page"
              value={lpUrl}
              onChange={(e) => setLpUrl(e.target.value)}
              disabled={isAnalyzing}
              required
              className="bg-white"
            />
          </div>
        </div>

        {/* Target Audience and Campaign Goal */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            type="text"
            placeholder="Zielgruppe (z.B. B2B Entscheider, 35-50 Jahre)"
            value={targetAudience}
            onChange={(e) => setTargetAudience(e.target.value)}
            disabled={isAnalyzing}
            className="bg-white"
          />

          <Input
            type="text"
            placeholder="Kampagnenziel (z.B. Lead-Generierung, Brand Awareness)"
            value={campaignGoal}
            onChange={(e) => setCampaignGoal(e.target.value)}
            disabled={isAnalyzing}
            className="bg-white"
          />
        </div>
      </div>

      {showAdvanced && (
        <Textarea
          placeholder='Brand Guidelines (JSON, optional)&#10;z.B. {"tone_of_voice": ["professionell"], "prohibited_words": ["billig"]}'
          value={guidelines}
          onChange={(e) => setGuidelines(e.target.value)}
          disabled={isAnalyzing}
          rows={3}
          className="bg-white font-mono text-xs"
        />
      )}

      <div className="flex items-center justify-between gap-3 pt-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setShowAdvanced(!showAdvanced)}
          disabled={isAnalyzing}
          className="text-sm"
        >
          {showAdvanced ? "Weniger Optionen" : "Brand Guidelines"}
        </Button>

        <Button
          type="submit"
          disabled={isAnalyzing || !lpUrl.trim() || !adFile}
          className="px-6"
          size="default"
        >
          {isAnalyzing ? (
            <>
              <span className="animate-spin mr-2">⏳</span>
              Analysiere...
            </>
          ) : (
            "Analyse starten"
          )}
        </Button>
      </div>
    </form>
  );
}
