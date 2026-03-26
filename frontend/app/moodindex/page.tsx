"use client";

import React, { useState, useEffect, useRef, FormEvent, memo } from 'react';
import { Loader2, Send, Plus, MessageSquare, Edit2, Trash2, Check, X, Mic } from 'lucide-react';
import { cn } from "../../lib/utils";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiClient } from "@/lib/api";
import VoiceModal from "@/components/VoiceModal";

interface Message {
  id: string;
  text: string;
  senderId: string;
  timestamp: Date;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

interface StoredMessage {
  id: string;
  text: string;
  senderId: string;
  timestamp: string;
}

interface StoredSession {
  id: string;
  title: string;
  messages: StoredMessage[];
  createdAt: string;
  updatedAt: string;
}

const getOrCreateUserId = (): string => {
  if (typeof window === 'undefined') return 'anonymous';
  const stored = localStorage.getItem('user_id');
  if (stored) return stored;
  const newId = (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function')
    ? crypto.randomUUID()
    : `anon-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  localStorage.setItem('user_id', newId);
  return newId;
};
const USER_ID = getOrCreateUserId();
const BOT_ID = 'bot';
const SESSIONS_STORAGE_KEY = 'wellness_coach_sessions';

const generateId = () =>
  (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function')
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

const BOT_GREETING: Message = {
  id: generateId(),
  text: 'Hello! I\'m your Wellness Coach. How can I support your emotional well-being today?',
  senderId: BOT_ID,
  timestamp: new Date(),
};

const ChatMessage = memo(({ message, isCurrentUser }: { message: Message; isCurrentUser: boolean }) => {
  return (
    <div
      className={cn(
        "flex w-full px-4 py-4 transition-colors",
        isCurrentUser ? "justify-end" : "justify-start"
      )}
    >
      {/* Content Container */}
      <div className={cn(
        "flex flex-col gap-1.5",
        isCurrentUser ? "items-end max-w-[75%]" : "items-start w-full"
      )}>
        {/* Label and Timestamp */}
        <div className="flex items-center gap-2 px-1">
          {isCurrentUser && (
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              You
            </span>
          )}
        </div>

        {/* Bubble for user; plain text for coach */}
        <div
          className={cn(
            "text-sm leading-relaxed",
            isCurrentUser
              ? "relative px-4 py-2.5 shadow-sm bg-muted text-foreground rounded-2xl rounded-tr-none"
              : "text-foreground w-full"
          )}
        >
          {message.text}
        </div>
        
        {/* Subtle timestamp (optional) */}
        <span className="text-[10px] text-muted-foreground/60 px-1">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
});
ChatMessage.displayName = 'ChatMessage';

const SessionItem = memo(({ 
  session, 
  isActive, 
  onSelect, 
  onDelete, 
  onRename 
}: { 
  session: ChatSession; 
  isActive: boolean; 
  onSelect: () => void;
  onDelete: () => void;
  onRename: (newTitle: string) => void;
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(session.title);

  const handleSaveEdit = () => {
    if (editTitle.trim()) {
      onRename(editTitle.trim());
      setIsEditing(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(session.title);
    setIsEditing(false);
  };

  return (
    <div
      className={cn(
        "group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors",
        isActive 
          ? "bg-muted" 
          : "hover:bg-muted/50"
      )}
      onClick={!isEditing ? onSelect : undefined}
    >
      <MessageSquare className="h-4 w-4 shrink-0" />
      {isEditing ? (
        <div className="flex-1 flex items-center gap-1">
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="h-7 text-sm"
            autoFocus
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSaveEdit();
              if (e.key === 'Escape') handleCancelEdit();
            }}
          />
          <Button
            size="icon"
            variant="ghost"
            className="h-7 w-7"
            onClick={handleSaveEdit}
          >
            <Check className="h-3 w-3" />
          </Button>
          <Button
            size="icon"
            variant="ghost"
            className="h-7 w-7"
            onClick={handleCancelEdit}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      ) : (
        <>
          <span className="flex-1 text-sm truncate">{session.title}</span>
          <div className="hidden group-hover:flex items-center gap-1">
            <Button
              size="icon"
              variant="ghost"
              className="h-7 w-7"
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(true);
              }}
            >
              <Edit2 className="h-3 w-3" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-7 w-7"
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
});
SessionItem.displayName = 'SessionItem';

const WellnessCoach = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Load sessions from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(SESSIONS_STORAGE_KEY);
    if (stored) {
      try {
        const parsed: StoredSession[] = JSON.parse(stored);
        const loadedSessions: ChatSession[] = parsed.map((s) => ({
          id: s.id,
          title: s.title,
          createdAt: new Date(s.createdAt),
          updatedAt: new Date(s.updatedAt),
          messages: s.messages.map((m) => ({
            id: m.id,
            text: m.text,
            senderId: m.senderId,
            timestamp: new Date(m.timestamp)
          }))
        }));
        setSessions(loadedSessions);
        if (loadedSessions.length > 0) {
          setCurrentSessionId(loadedSessions[0].id);
        } else {
          createNewSession();
        }
      } catch (e) {
        console.error('Failed to load sessions:', e);
        createNewSession();
      }
    } else {
      createNewSession();
    }
  }, []);

  // Save sessions to localStorage
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(sessions));
    }
  }, [sessions]);

  const createNewSession = () => {
    const newSession: ChatSession = {
      id: generateId(),
      title: 'New Conversation',
      messages: [{ ...BOT_GREETING, timestamp: new Date() }],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
  };

  const deleteSession = (sessionId: string) => {
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== sessionId);
      if (currentSessionId === sessionId) {
        if (filtered.length > 0) {
          setCurrentSessionId(filtered[0].id);
        } else {
          createNewSession();
        }
      }
      return filtered;
    });
  };

  const renameSession = (sessionId: string, newTitle: string) => {
    setSessions(prev =>
      prev.map(s =>
        s.id === sessionId ? { ...s, title: newTitle, updatedAt: new Date() } : s
      )
    );
  };

  const currentSession = sessions.find(s => s.id === currentSessionId);

  const handleVoiceMessageReceived = (transcript: string, audioUrl?: string) => {
    if (!currentSessionId) return;

    // Add user voice message
    const userVoiceMessage: Message = {
      id: generateId(),
      text: `🎤 ${transcript}`,
      senderId: USER_ID,
      timestamp: new Date(),
    };

    setSessions(prev =>
      prev.map(s => {
        if (s.id === currentSessionId) {
          return { ...s, messages: [...s.messages, userVoiceMessage], updatedAt: new Date() };
        }
        return s;
      })
    );

    // Optionally auto-close modal after receiving voice message
    // setIsVoiceModalOpen(false);
  };

  const scrollToBottom = () => {
    if (typeof window === 'undefined') return;
    requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages.length]);

  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() === '' || loading || !currentSessionId) return;

    const newMessage: Message = {
      id: generateId(),
      text: input,
      senderId: USER_ID,
      timestamp: new Date(),
    };

    // Update session with user message
    setSessions(prev =>
      prev.map(s => {
        if (s.id === currentSessionId) {
          const updatedMessages = [...s.messages, newMessage];
          // Auto-rename first session based on first user message
          const title = s.messages.length === 1 ? input.slice(0, 30) + (input.length > 30 ? '...' : '') : s.title;
          return { ...s, messages: updatedMessages, title, updatedAt: new Date() };
        }
        return s;
      })
    );

    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      const data = await apiClient.chat(currentSessionId, currentInput, { user_id: USER_ID });
      // Response structure: { response: { text, tasks, citations, ... } }
      const responseText = data?.response?.text || data?.text || "Thanks for reaching out. What's been on your mind lately?";
      const botResponse: Message = {
        id: generateId(),
        text: responseText,
        senderId: BOT_ID,
        timestamp: new Date(),
      };

      setSessions(prev =>
        prev.map(s =>
          s.id === currentSessionId
            ? { ...s, messages: [...s.messages, botResponse], updatedAt: new Date() }
            : s
        )
      );
    } catch (error) {
      console.error('Chat API failed:', error);
      const fallbackResponse: Message = {
        id: generateId(),
        text: "I'm having trouble connecting right now, but I want you to know that your feelings matter and support is available.",
        senderId: BOT_ID,
        timestamp: new Date(),
      };

      setSessions(prev =>
        prev.map(s =>
          s.id === currentSessionId
            ? { ...s, messages: [...s.messages, fallbackResponse], updatedAt: new Date() }
            : s
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div
        className={cn(
          "border-r bg-muted/30 flex flex-col transition-all duration-300",
          sidebarOpen ? "w-64" : "w-0"
        )}
      >
        {sidebarOpen && (
          <>
            <div className="p-3 border-b">
              <Button
                onClick={createNewSession}
                className="w-full justify-start gap-2"
                variant="outline"
              >
                <Plus className="h-4 w-4" />
                New Chat
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {sessions.map(session => (
                <SessionItem
                  key={session.id}
                  session={session}
                  isActive={session.id === currentSessionId}
                  onSelect={() => setCurrentSessionId(session.id)}
                  onDelete={() => deleteSession(session.id)}
                  onRename={(newTitle) => renameSession(session.id, newTitle)}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b p-4 flex items-center gap-3">
          <Button
            size="icon"
            variant="ghost"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <MessageSquare className="h-5 w-5" />
          </Button>
          <div className="flex-1">
            <h1 className="text-lg font-semibold">Wellness Coach</h1>
            <p className="text-sm text-muted-foreground">Your AI companion for emotional well-being</p>
          </div>
        </div>

        {/* Messages */}
        <div ref={listRef} className="flex-1 overflow-y-auto">
          {currentSession && currentSession.messages.length > 0 ? (
            <div className="max-w-3xl mx-auto w-full">
              {currentSession.messages.map((msg) => (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  isCurrentUser={msg.senderId === USER_ID}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4 p-8">
                <h2 className="text-2xl font-semibold">Welcome to Wellness Coach</h2>
                <p className="text-muted-foreground max-w-md">
                  Start a conversation to explore your feelings and receive personalized wellness guidance.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t p-4">
          <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto w-full">
            <div className="flex items-end gap-2">
              <Button
                type="button"
                size="icon"
                variant="outline"
                onClick={() => setIsVoiceModalOpen(true)}
                disabled={loading}
                className="h-11 w-11 shrink-0"
                title="Voice chat"
              >
                <Mic className="h-5 w-5" />
              </Button>
              <div className="flex-1 relative">
                <Input
                  placeholder="Message Wellness Coach..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={loading}
                  className="pr-12 min-h-11 resize-none"
                />
              </div>
              <Button
                size="icon"
                type="submit"
                disabled={loading || input.trim() === ''}
                className="h-11 w-11 shrink-0"
              >
                {loading ? <Loader2 className="animate-spin h-5 w-5" /> : <Send className="h-5 w-5" />}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground text-center mt-2">
              AI can make mistakes. Consider checking important information.
            </p>
          </form>
        </div>

        {/* Voice Modal */}
        {currentSessionId && (
          <VoiceModal
            isOpen={isVoiceModalOpen}
            onClose={() => setIsVoiceModalOpen(false)}
            sessionId={currentSessionId}
            onVoiceMessageReceived={handleVoiceMessageReceived}
            userId={USER_ID}
          />
        )}
      </div>
    </div>
  );
};

export default WellnessCoach;