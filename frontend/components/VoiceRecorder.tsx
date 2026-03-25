'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Mic, Square, Loader2 } from 'lucide-react';

interface VoiceRecorderProps {
  isRecording?: boolean;
  isProcessing?: boolean;
  onRecordingStart?: () => void;
  onRecordingEnd?: () => void;
  onAudioSubmit?: (audioBlob: Blob) => void;
  onRecordingComplete?: (audioBlob: Blob) => void;
  isOpen?: boolean;
  sessionId?: string;
}

export default function VoiceRecorder({
  isRecording: externalIsRecording,
  isProcessing = false,
  onRecordingStart,
  onRecordingEnd,
  onAudioSubmit,
  onRecordingComplete,
}: VoiceRecorderProps) {
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const stream = useRef<MediaStream | null>(null);
  const chunks = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [permission, setPermission] = useState<'granted' | 'denied' | 'prompt'>('prompt');
  const timerInterval = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (externalIsRecording !== undefined) {
      setIsRecording(externalIsRecording);
    }
  }, [externalIsRecording]);

  useEffect(() => {
    navigator.permissions.query({ name: 'microphone' }).then(permissionStatus => {
      setPermission(permissionStatus.state as 'granted' | 'denied' | 'prompt');
      permissionStatus.onchange = () => {
        setPermission(permissionStatus.state as 'granted' | 'denied' | 'prompt');
      };
    });
  }, []);

  const startRecording = async () => {
    try {
      if (permission === 'denied') {
        alert('Microphone permission denied. Please enable it in your browser settings.');
        return;
      }

      stream.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream.current);
      chunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        chunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(chunks.current, { type: 'audio/webm' });
        if (onRecordingComplete) {
          onRecordingComplete(audioBlob);
        } else if (onAudioSubmit) {
          onAudioSubmit(audioBlob);
        }

        // Clean up
        stream.current?.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      onRecordingStart?.();

      // Start timer
      timerInterval.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (err) {
      console.error('Microphone access error:', err);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      onRecordingEnd?.();

      if (timerInterval.current) {
        clearInterval(timerInterval.current);
      }
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (permission === 'denied') {
    return (
      <div className="flex flex-col items-center justify-center py-8 space-y-4">
        <div className="text-center space-y-2">
          <p className="text-sm font-medium">Microphone Permission Denied</p>
          <p className="text-xs text-muted-foreground">
            Please enable microphone access in your browser settings to use voice chat.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center space-y-6 py-6">
      {/* Recording Indicator */}
      {isRecording && (
        <div className="flex items-center gap-3 p-3 bg-destructive/10 rounded-lg">
          <div className="h-2 w-2 rounded-full bg-destructive animate-pulse" />
          <span className="text-sm font-medium">Recording: {formatTime(recordingTime)}</span>
        </div>
      )}

      {/* Visualizer / Waveform */}
      {isRecording && (
        <div className="flex items-center gap-1 h-12 px-4 bg-muted rounded-lg w-full max-w-sm justify-center">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="flex-1 h-1 bg-primary rounded-full"
              style={{
                animation: `pulse 0.6s ease-in-out infinite`,
                animationDelay: `${i * 0.05}s`,
                height: `${8 + Math.sin(i) * 4}px`,
              }}
            />
          ))}
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex gap-4">
        {!isRecording ? (
          <Button
            onClick={startRecording}
            disabled={isProcessing}
            size="lg"
            className="rounded-full h-16 w-16 p-0"
          >
            <Mic className="h-7 w-7" />
          </Button>
        ) : (
          <Button
            onClick={stopRecording}
            variant="destructive"
            size="lg"
            className="rounded-full h-16 w-16 p-0"
          >
            <Square className="h-5 w-5" />
          </Button>
        )}
      </div>

      {/* Status Text */}
      <p className="text-sm text-muted-foreground text-center">
        {isProcessing ? (
          <span className="flex items-center gap-2 justify-center">
            <Loader2 className="h-4 w-4 animate-spin" />
            Processing audio...
          </span>
        ) : isRecording ? (
          'Click the square button to stop recording'
        ) : (
          'Click the microphone to start recording'
        )}
      </p>
    </div>
  );
}
