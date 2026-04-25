"use client";
// components/RecommendationCard.tsx
// Displays the recommended song with Spotify embed player and play/skip/replay controls.

import { motion, AnimatePresence } from "framer-motion";
import { useRef, useEffect } from "react";
import type { Song, Reaction } from "../lib/api";

interface Props {
  song: Song | null;
  loading: boolean;
  lastReward: number | null;
  totalSteps: number;
  avgReward: number;
  onRecommend: () => void;
  onFeedback: (r: Reaction) => void;
}

const reactionButtons: { reaction: Reaction; emoji: string; label: string; color: string }[] = [
  { reaction: "listen", emoji: "▶️", label: "Play",   color: "btn-green" },
  { reaction: "skip",   emoji: "⏭",  label: "Skip",   color: "btn-red" },
  { reaction: "replay", emoji: "🔁", label: "Replay", color: "btn-cyan" },
];

function StatBadge({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="text-center">
      <p className="text-xs text-gray-500 uppercase tracking-widest">{label}</p>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  );
}

export default function RecommendationCard({
  song,
  loading,
  lastReward,
  totalSteps,
  avgReward,
  onRecommend,
  onFeedback,
}: Props) {
  const autoFeedbackSent = useRef(false);

  useEffect(() => {
    // Reset feedback tracker when song changes
    autoFeedbackSent.current = false;
  }, [song]);

  const handleAudioPlay = () => {
    if (!autoFeedbackSent.current) {
      onFeedback("listen");
      autoFeedbackSent.current = true;
    }
  };

  const handleAudioEnded = () => {
    // maybe record skip if they didn't finish? The prompt just said "plays or skips".
    // We already recorded play, so we don't need to do anything here unless they replay.
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="glass-card p-6 space-y-6"
    >
      <h2 className="text-xl font-bold text-white tracking-wide uppercase">
        🎵 Recommendation
      </h2>

      {/* Song display */}
      <div className="relative min-h-[120px] flex items-center justify-center">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-3"
            >
              <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
              <p className="text-gray-400 text-sm">Finding your vibe…</p>
            </motion.div>
          ) : song ? (
            <motion.div
              key={song.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="w-full text-center space-y-3"
            >
              {song.album_art ? (
                <img
                  src={song.album_art}
                  alt={`${song.title} album art`}
                  className="w-24 h-24 mx-auto rounded-none border border-[#333] shadow-lg object-cover"
                />
              ) : (
                <div className="w-24 h-24 mx-auto rounded-none bg-[#111] border border-[#333] flex items-center justify-center text-4xl shadow-lg">
                  🎶
                </div>
              )}

              <p className="text-2xl font-bold text-white mt-2">{song.title}</p>
              <p className="text-gray-400">{song.artist}</p>
              {song.album && (
                <p className="text-gray-500 text-xs italic">{song.album}</p>
              )}

              <div className="flex justify-center gap-2 flex-wrap mt-1">
                <span className="px-2 py-0.5 rounded-none bg-white/5 text-gray-400 text-xs">{song.genre}</span>
                <span className="px-2 py-0.5 rounded-none bg-white/5 text-gray-400 text-xs">{song.bpm} BPM</span>
                {song.tags.map((tag) => (
                  <span key={tag} className="px-2 py-0.5 rounded-none bg-[#FF3B00]/10 text-[#FF3B00] text-xs">
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Spotify Embed Player — plays 30s preview (or full if user is logged into Spotify) */}
              {song.embed_url ? (
                <div className="mt-4 rounded-xl overflow-hidden">
                  <iframe
                    src={song.embed_url}
                    width="100%"
                    height="80"
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                    loading="lazy"
                    style={{ border: "none", borderRadius: "12px" }}
                    title={`Play ${song.title}`}
                  />
                </div>
              ) : song.preview_url ? (
                <div className="mt-4">
                  <audio 
                    controls 
                    src={song.preview_url} 
                    className="w-full h-10 rounded-none grayscale" 
                    onPlay={handleAudioPlay}
                    onEnded={handleAudioEnded}
                  />
                </div>
              ) : null}

              {/* Open in Spotify link */}
              {song.external_url && (
                <a
                  href={song.external_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-[#1DB954] hover:text-[#1ed760] transition-colors mt-1"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                  </svg>
                  Open in Spotify
                </a>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center"
            >
              <p className="text-5xl mb-3">🎧</p>
              <p className="text-gray-400">Set your context and get a recommendation</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Feedback buttons */}
      <div className={`flex gap-3 ${!song ? "opacity-40 pointer-events-none" : ""}`}>
        {reactionButtons.map(({ reaction, emoji, label, color }) => (
          <motion.button
            key={reaction}
            whileHover={{ scale: 1.07 }}
            whileTap={{ scale: 0.93 }}
            onClick={() => {
              if (reaction === "skip" && !autoFeedbackSent.current) {
                // If they manually skip, mark it so we don't accidentally send play
                autoFeedbackSent.current = true;
              }
              onFeedback(reaction);
            }}
            className={`flex-1 py-3 rounded-none font-semibold text-sm transition-all ${color}`}
          >
            {emoji} {label}
          </motion.button>
        ))}
      </div>

      {/* Get recommendation button */}
      <motion.button
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        onClick={onRecommend}
        disabled={loading}
        className="w-full py-3 rounded-none font-bold bg-[#1D00FF] text-white tracking-wide transition-shadow disabled:opacity-50 uppercase"
      >
        ✨ Get Recommendation
      </motion.button>

      {/* Reward flash */}
      <AnimatePresence>
        {lastReward !== null && (
          <motion.div
            key={`reward-${totalSteps}`}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className={`text-center text-sm font-semibold ${
              lastReward > 0 ? "text-[#FF3B00]" : "text-gray-500"
            }`}
          >
            {lastReward > 0 ? "+" : ""}{lastReward} reward
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 pt-2 border-t border-white/5">
        <StatBadge label="Steps" value={totalSteps} />
        <StatBadge label="Avg Reward" value={avgReward.toFixed(3)} />
        <StatBadge
          label="Status"
          value={totalSteps === 0 ? "–" : avgReward > 0.5 ? "🔥" : avgReward > 0 ? "🙂" : "😬"}
        />
      </div>
    </motion.div>
  );
}
