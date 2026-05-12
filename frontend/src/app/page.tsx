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

  return (
    <div className="bg-background text-on-surface font-sans overflow-hidden h-screen flex">
      {/* Sidebar */}
      <aside className="h-full w-72 hidden md:flex flex-col border-r border-outline-variant/10 bg-[#080b08] z-50">
        <div className="flex flex-col h-full p-6">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-primary">Grow RAG</h1>
            <p className="text-[10px] text-on-surface-variant uppercase tracking-widest mt-1">Enterprise Tier</p>
          </div>

          <div className="space-y-3 mb-10">
            <button
              onClick={resetToWelcome}
              className="w-full bg-primary/10 border-l-4 border-primary text-primary flex items-center gap-3 px-4 py-3 hover:bg-primary/20 transition-all"
            >
              <span className="material-symbols-outlined">add_comment</span>
              <span className="font-semibold">New Chat</span>
            </button>
            <button
              onClick={clearChat}
              className="w-full text-on-surface-variant flex items-center gap-3 px-4 py-3 hover:bg-surface-variant/30 transition-all border border-outline-variant/10 rounded-lg text-sm"
            >
              <span className="material-symbols-outlined">delete</span>
              <span>Clear History</span>
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto">
            <div className="px-2">
              <p className="text-[10px] text-on-surface-variant uppercase tracking-widest mb-4">Ingested Schemes</p>
              <div className="space-y-3">
                {schemes.map((s) => (
                  <div
                    key={s.id}
                    onClick={() => setInputText(`Tell me about ${s.name}`)}
                    className="flex items-center gap-3 px-4 py-2 rounded-lg text-on-surface-variant hover:bg-surface-variant/30 cursor-pointer transition-all overflow-hidden"
                  >
                    <span className="text-xs truncate">{s.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </nav>

          <div className="mt-auto pt-6 border-t border-outline-variant/10">
            <div className="glass-panel rounded-xl p-4 flex items-center gap-3 bg-surface/50">
              <div className="h-10 w-10 rounded-lg bg-primary/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary">person</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold truncate">Enterprise User</p>
                <p className="text-[9px] text-primary uppercase font-bold tracking-tighter">Verified Node</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col relative overflow-hidden h-full">
        {/* Top AppBar */}
        <header className="fixed top-0 w-full z-40 backdrop-blur-2xl border-b border-outline-variant/10 flex justify-between items-center h-12 px-6 md:pl-80 bg-surface/80">
          <div className="flex items-center gap-6">
            <span className="text-lg font-bold text-primary">Grow RAG</span>
            <div className="hidden lg:flex items-center gap-4">
              <a className="text-[10px] uppercase tracking-wider text-on-surface-variant hover:text-primary" href="#">Models</a>
              <a className="text-[10px] uppercase tracking-wider text-on-surface-variant hover:text-primary" href="#">API</a>
              <a className="text-[10px] uppercase tracking-wider text-on-surface-variant hover:text-primary" href="#">Docs</a>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-3 py-0.5 bg-primary/10 border border-primary/20 rounded-full text-[9px] uppercase tracking-wider text-primary">
              Facts-only mode
            </div>
            <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-xl">notifications</span>
            <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-xl">account_circle</span>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 pt-12 pb-24 flex flex-col relative overflow-hidden h-full">
          <div className="flex-1 flex overflow-hidden h-full">
            {view === "welcome" ? (
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
                <div className="mb-8 p-1 rounded-2xl bg-surface-variant border border-outline-variant/20">
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center ai-pulse">
                    <span className="material-symbols-outlined text-surface text-3xl font-bold">hub</span>
                  </div>
                </div>
                <h2 className="text-4xl font-bold text-on-surface mb-4 tracking-tight">
                  Enterprise <span className="text-primary">Intelligence</span>.
                </h2>
                <p className="text-on-surface-variant text-sm max-w-xl mx-auto leading-relaxed mb-8">
                  Standardized RAG interface for HDFC Mutual Fund analysis.
                  Cite-verified factual compliance engine.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl w-full">
                  <div onClick={() => setInputText("What is the expense ratio of HDFC Mid Cap?")} className="p-4 rounded-xl border border-outline-variant/10 hover:border-primary/30 cursor-pointer group bg-surface/30">
                    <span className="material-symbols-outlined text-primary mb-2">percent</span>
                    <h3 className="text-on-surface text-xs font-semibold">Expense Ratio</h3>
                  </div>
                  <div onClick={() => setInputText("What is the exit load of HDFC Equity Fund?")} className="p-4 rounded-xl border border-outline-variant/10 hover:border-primary/30 cursor-pointer group bg-surface/30">
                    <span className="material-symbols-outlined text-secondary mb-2">payments</span>
                    <h3 className="text-on-surface text-xs font-semibold">Exit Load</h3>
                  </div>
                  <div onClick={() => setInputText("What is the lock-in period for HDFC ELSS?")} className="p-4 rounded-xl border border-outline-variant/10 hover:border-primary/30 cursor-pointer group bg-surface/30">
                    <span className="material-symbols-outlined text-primary mb-2">lock_clock</span>
                    <h3 className="text-on-surface text-xs font-semibold">ELSS Lock-in</h3>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto px-6 py-10 max-w-4xl mx-auto w-full space-y-8 scroll-smooth">
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex gap-6 ${msg.sender === "user" ? "max-w-3xl" : ""}`}>
                      {msg.sender === "user" ? (
                        <>
                          <div className="h-10 w-10 shrink-0 rounded-lg bg-surface-container p-2 flex items-center justify-center border border-outline-variant/10">
                            <span className="material-symbols-outlined text-on-surface-variant">person</span>
                          </div>
                          <div className="space-y-2">
                            <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">YOU • {msg.time}</p>
                            <div className="text-sm text-on-surface leading-relaxed">{msg.text}</div>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="h-10 w-10 shrink-0 rounded-lg bg-primary-container p-2 flex items-center justify-center relative overflow-hidden">
                            <div className="ai-pulse absolute inset-0 opacity-40"></div>
                            <span className="material-symbols-outlined text-on-primary-container relative z-10">smart_toy</span>
                          </div>
                          <div className="flex-1 space-y-4">
                            <p className="text-[10px] text-primary uppercase tracking-widest font-bold">GROW AI • {msg.time}</p>
                            <div className="bot-msg-bubble glass-panel">
                              <div className="text-sm text-on-surface leading-relaxed">
                                {msg.text.split("\n").map((line, i) => <p key={i}>{line}</p>)}
                              </div>
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                  {isProcessing && (
                    <div className="flex gap-6">
                      <div className="h-10 w-10 shrink-0 rounded-lg bg-primary-container p-2 flex items-center justify-center relative overflow-hidden">
                        <div className="ai-pulse absolute inset-0 opacity-40"></div>
                        <span className="material-symbols-outlined text-on-primary-container relative z-10">smart_toy</span>
                      </div>
                      <div className="flex-1 space-y-4">
                        <p className="text-[10px] text-primary uppercase tracking-widest font-bold">GROW AI • THINKING...</p>
                        <div className="bot-msg-bubble glass-panel">
                          <div className="space-y-3 opacity-30">
                            <div className="h-2 w-full bg-primary/20 rounded-full animate-pulse"></div>
                            <div className="h-2 w-3/4 bg-primary/20 rounded-full animate-pulse"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </div>
            )}

            {/* Right Panel: Sources */}
            <aside className={`hidden xl:flex w-80 h-full flex-col border-l border-outline-variant/10 bg-[#0c120c] p-6 gap-6 transition-all duration-300 ${activeSources.length > 0 ? "" : "opacity-0"}`}>
              <div className="flex items-center justify-between">
                <h3 className="text-on-surface font-semibold flex items-center gap-2 text-sm">
                  <span className="material-symbols-outlined text-secondary text-base">description</span>
                  Sources
                </h3>
              </div>
              <div className="space-y-4">
                {activeSources.map((source, i) => (
                  <div key={i} className="p-4 rounded-xl bg-surface/50 border border-outline-variant/10 relative overflow-hidden group hover:border-secondary transition-all">
                    <div className="flex justify-between items-start mb-2">
                      <span className="px-2 py-0.5 bg-secondary/10 text-secondary text-[10px] rounded font-bold uppercase">Official Source</span>
                    </div>
                    <p className="text-xs font-semibold text-on-surface truncate">{source.scheme_name}</p>
                    <a href={source.url} target="_blank" className="mt-3 block text-[10px] text-blue-600 font-bold hover:underline">View on Groww.in →</a>
                  </div>
                ))}
              </div>
            </aside>
          </div>

          {/* Input Bar */}
          <div className="absolute bottom-0 left-0 right-0 p-6 pointer-events-none">
            <div className="max-w-4xl mx-auto w-full pointer-events-auto">
              <div className="glass-panel rounded-2xl p-2 flex items-end gap-2 shadow-2xl relative group border border-outline-variant/20 bg-surface/80">
                <button className="h-10 w-10 flex items-center justify-center rounded-xl text-on-surface-variant hover:text-primary">
                  <span className="material-symbols-outlined">attach_file</span>
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
                  className="flex-1 bg-transparent border-none focus:ring-0 text-on-surface placeholder:text-on-surface-variant/30 py-3 resize-none outline-none text-sm"
                  placeholder="Ask Grow RAG anything..."
                ></textarea>
                <button
                  onClick={handleSend}
                  disabled={isProcessing}
                  className="h-10 w-10 flex items-center justify-center rounded-xl bg-primary text-on-primary hover:shadow-[0_0_20px_rgba(75,226,119,0.3)] transition-all disabled:opacity-50"
                >
                  <span className="material-symbols-outlined">send</span>
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
