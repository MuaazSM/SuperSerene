'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import VoiceRecorder from '@/components/VoiceRecorder';
import AudioPlayer from '@/components/AudioPlayer';
import { Loader2, Volume2, VolumeX } from 'lucide-react';

interface TranscriptMessage {
  role: 'user' | 'assistant';
  text: string;
}

type VoiceMessageType =
  | 'processing'
  | 'response_complete'
  | 'error'
  | 'connection_established'
  | 'voices'
  | 'transcript'
  | 'unknown';

interface VoiceMessage {
  type: VoiceMessageType;
  error?: string;
  message?: string;
  voice_id?: string;
}

export default function VoiceChatPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [audioUrl, setAudioUrl] = useState<string>('');
  const [autoPlay, setAutoPlay] = useState(true);

  const ws = useRef<WebSocket | null>(null);
  const audioPlayer = useRef<HTMLAudioElement>(null);
  const transcriptEnd = useRef<HTMLDivElement>(null);

  // Initialize session
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const initSession = async () => {
      try {
        const response = await fetch('/api/v1/chat/sessions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: 'Voice Chat',
            type: 'voice_chat'
          })
        });

        if (response.ok) {
          const data = await response.json();
          setSessionId(data.session_id || data._id);
        }
      } catch (err) {
        console.error('Session error:', err);
        setErrorMessage('Failed to create session');
      }
    };

    initSession();
  }, [router]);

  const handleAudioResponse = useCallback((audioBlob: Blob) => {
    const url = URL.createObjectURL(audioBlob);
    setAudioUrl(url);
    if (autoPlay && audioPlayer.current) {
      audioPlayer.current.play();
    }
  }, [autoPlay]);

  // WebSocket connection
  useEffect(() => {
    if (!sessionId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/voice/${sessionId}`;

    try {
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setIsConnected(true);
        setErrorMessage('');
      };

      ws.current.onmessage = (event) => {
        try {
          if (event.data instanceof Blob) {
            handleAudioResponse(event.data);
          } else {
            const msg: VoiceMessage = JSON.parse(event.data);
            if (msg.type === 'processing') setIsProcessing(true);
            else if (msg.type === 'response_complete') setIsProcessing(false);
            else if (msg.type === 'error') {
              setErrorMessage(msg.error || 'Error processing audio');
              setIsProcessing(false);
            }
          }
        } catch (err) {
          console.error('Message error:', err);
        }
      };

      ws.current.onerror = () => {
        setErrorMessage('Connection error');
        setIsConnected(false);
      };

      ws.current.onclose = () => setIsConnected(false);

      return () => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.close();
        }
      };
    } catch (err) {
      setErrorMessage('Failed to connect');
    }
  }, [sessionId, handleAudioResponse]);

  const handleAudioSubmit = useCallback((audioBlob: Blob) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      setErrorMessage('Not connected');
      return;
    }

    setIsProcessing(true);
    setErrorMessage('');

    try {
      ws.current.send(audioBlob);
      ws.current.send(JSON.stringify({
        type: 'submit',
        format: 'webm'
      }));
    } catch (err) {
      console.error('Submit error:', err);
      setErrorMessage('Failed to send audio');
      setIsProcessing(false);
    }
  }, []);

  useEffect(() => {
    transcriptEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-3xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-1">Voice Chat</h1>
          <p className="text-sm text-muted-foreground">
            {isConnected ? '🟢 Connected' : '🔴 Connecting...'}
          </p>
        </div>

        {/* Transcript */}
        <div className="border rounded-lg bg-card p-4 mb-6 w-full min-h-64 max-h-96 overflow-y-auto">
          {transcript.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center text-muted-foreground">
              Start speaking to chat with your wellness coach
            </div>
          ) : (
            <div className="space-y-3">
              {transcript.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-3 py-2 rounded text-sm ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="flex gap-2 items-center text-xs text-muted-foreground">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    Processing...
                  </div>
                </div>
              )}
            </div>
          )}
          <div ref={transcriptEnd} />
        </div>

        {/* Error */}
        {errorMessage && (
          <div className="text-xs text-destructive mb-4 px-2">
            {errorMessage}
          </div>
        )}

        {/* Audio Player */}
        {audioUrl && (
          <div className="mb-6 p-4 border rounded-lg bg-card">
            <AudioPlayer ref={audioPlayer} src={audioUrl} autoPlay={autoPlay} />
          </div>
        )}

        {/* Controls */}
        <div className="flex gap-2 mb-6">
          <Button
            variant="outline"
            size="sm"
            className="min-h-[44px] min-w-[44px]"
            onClick={() => setAutoPlay(!autoPlay)}
          >
            {autoPlay ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="min-h-[44px]"
            onClick={() => {
              setTranscript([]);
              setAudioUrl('');
              setErrorMessage('');
            }}
          >
            Clear
          </Button>
        </div>

        {/* Voice Recorder */}
        <div className="border rounded-lg bg-card p-6">
          {isConnected ? (
            <VoiceRecorder
              isRecording={isRecording}
              isProcessing={isProcessing}
              onRecordingStart={() => setIsRecording(true)}
              onRecordingEnd={() => setIsRecording(false)}
              onAudioSubmit={handleAudioSubmit}
            />
          ) : (
            <div className="text-center text-sm text-muted-foreground">
              Connecting to voice service...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
