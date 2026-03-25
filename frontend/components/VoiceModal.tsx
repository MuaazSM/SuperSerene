"use client";

import React, { useState, useRef, useEffect } from 'react';
import { X, Mic, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import VoiceRecorder from '@/components/VoiceRecorder';
import AudioPlayer from '@/components/AudioPlayer';

interface VoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  onVoiceMessageReceived?: (transcript: string, audioUrl?: string) => void;
  userId?: string;
}

const VoiceModal: React.FC<VoiceModalProps> = ({ 
  isOpen, 
  onClose, 
  sessionId, 
  onVoiceMessageReceived,
  userId = 'user123' 
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [responseTranscript, setResponseTranscript] = useState('');
  const [userTranscript, setUserTranscript] = useState('');
  const [conversationHistory, setConversationHistory] = useState<Array<{
    type: 'user' | 'assistant';
    text: string;
    audioUrl?: string;
  }>>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const callbackRef = useRef(onVoiceMessageReceived);
  const transcriptRef = useRef(userTranscript);

  // Update refs when props change
  React.useEffect(() => {
    callbackRef.current = onVoiceMessageReceived;
    transcriptRef.current = userTranscript;
  }, [onVoiceMessageReceived, userTranscript]);

  // Initialize WebSocket connection
  useEffect(() => {
    if (!isOpen) return;

    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/voice/${sessionId}`;
      
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('Voice WebSocket connected');
          setConnectionStatus('connected');
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          if (data.type === 'transcript') {
            setUserTranscript(data.transcript);
            setResponseTranscript(data.transcript);
          } else if (data.type === 'complete') {
            setIsProcessing(false);
            if (data.transcript && callbackRef.current) {
              callbackRef.current(data.transcript, data.audio_base64);
              setConversationHistory(prev => [
                ...prev,
                { type: 'user', text: transcriptRef.current || data.transcript },
                { type: 'assistant', text: data.response_text || data.transcript, audioUrl: data.audio_base64 }
              ]);
              setUserTranscript('');
            }
          } else if (data.type === 'error') {
            console.error('Voice error:', data.error);
            setIsProcessing(false);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionStatus('disconnected');
        };

        ws.onclose = () => {
          console.log('Voice WebSocket disconnected');
          setConnectionStatus('disconnected');
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        setConnectionStatus('disconnected');
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isOpen, sessionId]);

  const handleRecordingComplete = async (audioBlob: Blob) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not ready', wsRef.current?.readyState);
      // Retry a few times
      let attempts = 0;
      const maxAttempts = 5;
      
      while ((!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 200));
        attempts++;
      }
      
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.error('WebSocket failed to connect after retries');
        return;
      }
    }

    setIsProcessing(true);
    setResponseTranscript('');

    try {
      const base64Audio = await blobToBase64(audioBlob);
      wsRef.current.send(JSON.stringify({
        type: 'audio',
        audio_base64: base64Audio,
        user_id: userId,
        format: 'webm'
      }));
    } catch (error) {
      console.error('Error processing audio:', error);
      setIsProcessing(false);
    }
  };

  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = (reader.result as string).split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  const handleEndConversation = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-background rounded-lg shadow-lg w-full max-w-2xl h-[600px] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="border-b p-4 flex items-center justify-between bg-muted/50">
          <div>
            <h2 className="font-semibold text-lg">Voice Chat</h2>
            <p className="text-xs text-muted-foreground mt-1">
              {connectionStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
            </p>
          </div>
          <Button
            size="icon"
            variant="ghost"
            onClick={handleEndConversation}
            className="h-8 w-8"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Conversation History */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {conversationHistory.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-3">
                <Mic className="h-12 w-12 mx-auto text-muted-foreground opacity-50" />
                <p className="text-muted-foreground">Start speaking to begin voice chat</p>
              </div>
            </div>
          ) : (
            conversationHistory.map((item, idx) => (
              <div
                key={idx}
                className={cn(
                  "flex",
                  item.type === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    "max-w-[75%] p-3 rounded-lg",
                    item.type === 'user'
                      ? 'bg-muted text-foreground rounded-br-none'
                      : 'bg-primary/10 text-foreground rounded-bl-none'
                  )}
                >
                  <p className="text-sm">{item.text}</p>
                  {item.audioUrl && item.type === 'assistant' && (
                    <div className="mt-2">
                      <AudioPlayer audioUrl={item.audioUrl} />
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Voice Recorder Section */}
        <div className="border-t p-4 bg-muted/30">
          {isProcessing ? (
            <div className="flex flex-col items-center justify-center py-6 space-y-3">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">
                {responseTranscript ? 'Processing your message...' : 'Listening...'}
              </p>
              {responseTranscript && (
                <div className="bg-background p-2 rounded text-xs text-foreground max-w-[90%] text-center">
                  {responseTranscript}
                </div>
              )}
            </div>
          ) : (
            <VoiceRecorder
              onRecordingComplete={handleRecordingComplete}
              isOpen={isOpen}
              sessionId={sessionId}
            />
          )}
        </div>

        {/* Footer */}
        <div className="border-t p-3 bg-muted/30 flex justify-between items-center">
          <p className="text-xs text-muted-foreground">
            {conversationHistory.length > 0 ? (
              <>
                <span className="font-medium">{conversationHistory.length}</span> messages in this session
              </>
            ) : (
              'Ready to chat'
            )}
          </p>
          <Button
            size="sm"
            onClick={handleEndConversation}
            variant="outline"
          >
            Done
          </Button>
        </div>
      </div>
    </div>
  );
};

export default VoiceModal;
