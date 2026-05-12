"use client";

import { useState, useEffect, useRef } from "react";

interface Scheme {
  id: string;
  name: string;
  category: string;
}

interface Source {
  scheme_name: string;
  url: string;
}

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  time: string;
  sources?: Source[];
}

export default function Home() {
  const [view, setView] = useState<"welcome" | "chat">("welcome");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [activeSources, setActiveSources] = useState<Source[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    fetch(`${API_URL}/meta`)
      .then((res) => res.json())
      .then((data) => setSchemes(data.schemes))
      .catch((err) => console.error("Failed to load meta:", err));
  }, [API_URL]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const query = input.trim();
    if (!query || isProcessing) return;

    setIsProcessing(true);
    setView("chat");
    const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    
    const userMsg: Message = {
      id: Date.now().toString(),
      text: query,
      sender: "user",
      time: now,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();
      
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: data.answer,
        sender: "bot",
        time: "JUST NOW",
        sources: data.sources,
      };

      setMessages((prev) => [...prev, botMsg]);
      if (data.sources && data.sources.length > 0) {
        setActiveSources(data.sources);
      }
    } catch (error) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: "Analysis failed. Please check your connection and try again.",
        sender: "bot",
        time: "JUST NOW",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetToWelcome = () => {
    setView("welcome");
    setMessages([]);
    setActiveSources([]);
    setInput("");
  };

  const clearChat = () => {
    setMessages([]);
    setActiveSources([]);
  };

  const setInputText = (text: string) => {
    setInput(text);
    inputRef.current?.focus();
  };

  const formatResponse = (text: string) => {
    return text.split("\n").map((line, i) => {
      // Bold text handling **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <p key={i} className="mb-2 last:mb-0">
          {parts.map((part, j) => {
            if (part.startsWith("**") && part.endsWith("**")) {
              return <strong key={j} className="text-primary font-bold">{part.slice(2, -2)}</strong>;
            }
            // URL handling
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            const urlParts = part.split(urlRegex);
            return urlParts.map((urlPart, k) => {
              if (urlPart.match(urlRegex)) {
                return (
                  <a key={k} href={urlPart} target="_blank" className="text-blue-400 underline hover:text-blue-300 transition-colors">
                    {urlPart}
                  </a>
                );
              }
              return urlPart;
            });
          })}
        </p>
      );
    });
  };

  return (
    <div className="bg-[#050705] text-on-surface font-sans overflow-hidden h-screen flex">
      {/* Sidebar */}
      <aside className="h-full w-72 hidden md:flex flex-col border-r border-outline-variant/10 bg-[#080b08] z-50">
        <div className="flex flex-col h-full p-6">
          <div className="mb-8">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <span className="material-symbols-outlined text-surface text-xl font-bold">hub</span>
              </div>
              <h1 className="text-xl font-bold text-on-surface tracking-tight">Grow RAG</h1>
            </div>
            <p className="text-[10px] text-primary uppercase tracking-[0.2em] mt-2 font-bold opacity-70">Enterprise Intelligence</p>
          </div>

          <div className="space-y-3 mb-10">
            <button
              onClick={resetToWelcome}
              className="w-full bg-primary text-surface flex items-center gap-3 px-4 py-3 rounded-xl hover:shadow-[0_0_20px_rgba(75,226,119,0.3)] transition-all"
            >
              <span className="material-symbols-outlined">add</span>
              <span className="font-bold text-sm">New Analysis</span>
            </button>
            <button
              onClick={clearChat}
              className="w-full text-on-surface-variant flex items-center gap-3 px-4 py-3 hover:bg-surface-variant/30 transition-all border border-outline-variant/10 rounded-xl text-sm"
            >
              <span className="material-symbols-outlined text-sm">delete</span>
              <span>Clear History</span>
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto custom-scrollbar">
            <div className="px-2">
              <p className="text-[10px] text-on-surface-variant uppercase tracking-widest mb-4 font-bold opacity-50">Ingested Schemes</p>
              <div className="space-y-2">
                {schemes.map((s) => (
                  <div
                    key={s.id}
                    onClick={() => setInputText(`Tell me about ${s.name}`)}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-on-surface-variant hover:text-primary hover:bg-primary/5 cursor-pointer transition-all overflow-hidden border border-transparent hover:border-primary/10"
                  >
                    <span className="material-symbols-outlined text-xs">account_balance</span>
                    <span className="text-[11px] font-medium truncate">{s.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </nav>

          <div className="mt-auto pt-6 border-t border-outline-variant/10">
            {/* User Profile Removed */}
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col relative overflow-hidden h-full bg-gradient-to-br from-[#050705] to-[#0a0f0a]">
        {/* Main Content */}
        <main className="flex-1 pt-8 pb-28 flex flex-col relative overflow-hidden h-full">
          <div className="flex-1 flex overflow-hidden h-full">
            {view === "welcome" ? (
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center animate-slide-up">
                <div className="mb-8 p-1 rounded-3xl bg-surface-variant border border-outline-variant/20 shadow-2xl">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-[#2d5c3a] flex items-center justify-center ai-pulse shadow-[0_0_40px_rgba(75,226,119,0.2)]">
                    <span className="material-symbols-outlined text-surface text-4xl font-bold">hub</span>
                  </div>
                </div>
                <h2 className="text-5xl font-bold text-on-surface mb-4 tracking-tighter">
                  How can I <span className="text-primary italic">help you today?</span>
                </h2>
                <p className="text-on-surface-variant text-base max-w-xl mx-auto leading-relaxed mb-10 opacity-70">
                  Standardized RAG interface for HDFC Mutual Fund analysis.<br/>
                  Cite-verified factual compliance engine.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl w-full">
                  <div onClick={() => setInputText("What is the expense ratio of HDFC Mid Cap?")} className="p-6 rounded-2xl border border-outline-variant/10 hover:border-primary/40 cursor-pointer group bg-surface/20 backdrop-blur-sm transition-all hover:translate-y-[-4px]">
                    <span className="material-symbols-outlined text-primary mb-3 text-2xl">percent</span>
                    <h3 className="text-on-surface text-sm font-bold">Expense Ratio</h3>
                    <p className="text-[10px] text-on-surface-variant mt-2">Check current fund management costs</p>
                  </div>
                  <div onClick={() => setInputText("What is the exit load of HDFC Equity Fund?")} className="p-6 rounded-2xl border border-outline-variant/10 hover:border-primary/40 cursor-pointer group bg-surface/20 backdrop-blur-sm transition-all hover:translate-y-[-4px]">
                    <span className="material-symbols-outlined text-secondary mb-3 text-2xl">payments</span>
                    <h3 className="text-on-surface text-sm font-bold">Exit Load</h3>
                    <p className="text-[10px] text-on-surface-variant mt-2">Verify redemption penalty terms</p>
                  </div>
                  <div onClick={() => setInputText("What is the lock-in period for HDFC ELSS?")} className="p-6 rounded-2xl border border-outline-variant/10 hover:border-primary/40 cursor-pointer group bg-surface/20 backdrop-blur-sm transition-all hover:translate-y-[-4px]">
                    <span className="material-symbols-outlined text-primary mb-3 text-2xl">lock_clock</span>
                    <h3 className="text-on-surface text-sm font-bold">ELSS Lock-in</h3>
                    <p className="text-[10px] text-on-surface-variant mt-2">Analyze tax-saver duration rules</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto px-6 py-10 max-w-4xl mx-auto w-full space-y-10 scroll-smooth custom-scrollbar">
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex w-full ${msg.sender === "user" ? "justify-end" : "justify-start"} animate-slide-up`}>
                      <div className={`flex gap-4 max-w-[85%] ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}>
                        {/* Icon */}
                        <div className={`h-9 w-9 shrink-0 rounded-xl flex items-center justify-center border border-outline-variant/10 ${msg.sender === "user" ? "bg-surface-container" : "bg-primary-container relative"}`}>
                          {msg.sender === "bot" && <div className="ai-pulse absolute inset-0 opacity-40"></div>}
                          <span className="material-symbols-outlined text-base">
                            {msg.sender === "user" ? "person" : "smart_toy"}
                          </span>
                        </div>
                        
                        {/* Content */}
                        <div className="flex flex-col space-y-1.5">
                          <p className={`text-[9px] uppercase tracking-[0.2em] font-bold opacity-40 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
                            {msg.sender === "user" ? "Verified User" : "Grow Intelligence Agent"} • {msg.time}
                          </p>
                          <div className={msg.sender === "user" ? "user-bubble" : "bot-bubble"}>
                            <div className="text-[13px] text-on-surface leading-[1.6]">
                              {formatResponse(msg.text)}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {isProcessing && (
                    <div className="flex w-full justify-start animate-slide-up">
                      <div className="flex gap-4 max-w-[85%]">
                        <div className="h-9 w-9 shrink-0 rounded-xl bg-primary-container p-2 flex items-center justify-center relative overflow-hidden">
                          <div className="ai-pulse absolute inset-0 opacity-40"></div>
                          <span className="material-symbols-outlined text-base text-on-primary-container relative z-10">smart_toy</span>
                        </div>
                        <div className="flex-1 space-y-2.5 pt-4">
                          <div className="h-1.5 w-48 bg-primary/20 rounded-full animate-pulse"></div>
                          <div className="h-1.5 w-32 bg-primary/20 rounded-full animate-pulse opacity-50"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </div>
            )}

            {/* Right Panel: Sources (Only show when there are sources) */}
            <aside className={`hidden ${activeSources.length > 0 ? "xl:flex" : "hidden"} w-80 h-full flex-col border-l border-outline-variant/10 bg-[#080b08] p-8 gap-8 transition-all duration-500`}>
              <div className="flex items-center justify-between">
                <h3 className="text-on-surface font-bold flex items-center gap-2 text-xs uppercase tracking-widest">
                  <span className="material-symbols-outlined text-primary text-lg">verified_user</span>
                  Sources
                </h3>
              </div>
              <div className="space-y-6">
                {activeSources.map((source, i) => (
                  <div key={i} className="p-5 rounded-2xl bg-surface/30 border border-outline-variant/10 relative overflow-hidden group hover:border-primary/30 transition-all shadow-xl">
                    <div className="flex justify-between items-start mb-3">
                      <span className="px-2 py-0.5 bg-primary/10 text-primary text-[9px] rounded font-bold uppercase tracking-wider">Official Data</span>
                    </div>
                    <p className="text-xs font-bold text-on-surface mb-4 leading-relaxed">{source.scheme_name}</p>
                    <a href={source.url} target="_blank" className="text-[10px] text-primary font-bold flex items-center gap-1 hover:gap-2 transition-all">
                      Open Verification Portal <span className="material-symbols-outlined text-xs">arrow_forward</span>
                    </a>
                  </div>
                ))}
              </div>
              <div className="mt-auto p-4 rounded-xl bg-primary/5 border border-primary/10 text-[9px] text-on-surface-variant leading-relaxed">
                <span className="font-bold text-primary">Compliance:</span> All data retrieved from official fund documents. Cross-verification recommended for high-stakes decisions.
              </div>
            </aside>
          </div>

          {/* Input Bar */}
          <div className="absolute bottom-0 left-0 right-0 p-8 pointer-events-none">
            <div className="max-w-4xl mx-auto w-full pointer-events-auto">
              <div className="glass-panel rounded-[24px] p-2.5 flex items-end gap-3 shadow-[0_20px_50px_rgba(0,0,0,0.5)] relative group border border-white/5 bg-surface/60">
                <button className="h-11 w-11 flex items-center justify-center rounded-xl text-on-surface-variant hover:text-primary hover:bg-primary/10 transition-all">
                  <span className="material-symbols-outlined text-xl">attach_file</span>
                </button>
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  rows={1}
                  className="flex-1 bg-transparent border-none focus:ring-0 text-on-surface placeholder:text-on-surface-variant/20 py-3 resize-none outline-none text-[15px] max-h-40"
                  placeholder="Ask Grow Intelligence Agent..."
                ></textarea>
                <button
                  onClick={handleSend}
                  disabled={isProcessing}
                  className="h-11 w-11 flex items-center justify-center rounded-xl bg-primary text-surface hover:shadow-[0_0_30px_rgba(75,226,119,0.4)] transition-all disabled:opacity-30 disabled:grayscale"
                >
                  <span className="material-symbols-outlined text-xl font-bold">send</span>
                </button>
              </div>
              <p className="text-center text-[9px] text-on-surface-variant mt-4 opacity-50 uppercase tracking-widest font-bold">
                Factual compliance node v1.0.2 • Standardized RAG Protocol
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
