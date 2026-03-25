'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';

interface AudioPlayerProps {
  ref?: React.Ref<HTMLAudioElement>;
  src?: string;
  audioUrl?: string;
  autoPlay?: boolean;
}

const AudioPlayer = React.forwardRef<HTMLAudioElement, AudioPlayerProps>(
  ({ src, audioUrl, autoPlay = false }, forwardedRef) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    const [isMuted, setIsMuted] = useState(false);
    const audioRef = useRef<HTMLAudioElement>(null);

    // Sync the forwarded ref with our internal ref
    React.useEffect(() => {
      if (forwardedRef) {
        if (typeof forwardedRef === 'function') {
          forwardedRef(audioRef.current);
        } else {
          forwardedRef.current = audioRef.current;
        }
      }
    }, [forwardedRef]);

    const audioSrc = audioUrl || src;

    useEffect(() => {
      const audio = audioRef.current;
      if (!audio) return;

      const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
      const handleLoadedMetadata = () => setDuration(audio.duration);
      const handleEnded = () => setIsPlaying(false);

      audio.addEventListener('timeupdate', handleTimeUpdate);
      audio.addEventListener('loadedmetadata', handleLoadedMetadata);
      audio.addEventListener('ended', handleEnded);

      return () => {
        audio.removeEventListener('timeupdate', handleTimeUpdate);
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audio.removeEventListener('ended', handleEnded);
      };
    }, []);

    useEffect(() => {
      if (autoPlay && audioRef.current && audioSrc) {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }, [audioSrc, autoPlay]);

    const togglePlay = () => {
      if (!audioRef.current) return;

      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    };

    const toggleMute = () => {
      if (audioRef.current) {
        audioRef.current.muted = !isMuted;
        setIsMuted(!isMuted);
      }
    };

    const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newVolume = parseFloat(e.target.value);
      setVolume(newVolume);
      if (audioRef.current) {
        audioRef.current.volume = newVolume;
      }
    };

    const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newTime = parseFloat(e.target.value);
      if (audioRef.current) {
        audioRef.current.currentTime = newTime;
      }
      setCurrentTime(newTime);
    };

    const formatTime = (time: number) => {
      if (!isFinite(time)) return '0:00';
      const minutes = Math.floor(time / 60);
      const seconds = Math.floor(time % 60);
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    return (
      <>
        <audio ref={audioRef} src={audioSrc} />
        <div className="flex flex-col gap-3 w-full">
          {/* Progress Bar */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground w-8 text-right">
              {formatTime(currentTime)}
            </span>
            <input
              type="range"
              min="0"
              max={duration || 0}
              value={currentTime}
              onChange={handleProgressChange}
              className="flex-1 h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <span className="text-xs text-muted-foreground w-8">
              {formatTime(duration)}
            </span>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-3">
            {/* Play/Pause Button */}
            <Button
              size="icon"
              variant="outline"
              onClick={togglePlay}
              className="h-8 w-8 shrink-0"
            >
              {isPlaying ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4" />
              )}
            </Button>

            {/* Volume Control */}
            <Button
              size="icon"
              variant="ghost"
              onClick={toggleMute}
              className="h-8 w-8 shrink-0"
            >
              {isMuted || volume === 0 ? (
                <VolumeX className="h-4 w-4" />
              ) : (
                <Volume2 className="h-4 w-4" />
              )}
            </Button>

            {/* Volume Slider */}
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-20 h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
            />

            <span className="text-xs text-muted-foreground w-8">
              {Math.round(isMuted ? 0 : volume * 100)}%
            </span>
          </div>
        </div>
      </>
    );
  }
);

AudioPlayer.displayName = 'AudioPlayer';

export default AudioPlayer;
