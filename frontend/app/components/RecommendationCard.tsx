"use client";
// components/RecommendationCard.tsx
// Displays the recommended song and play/skip/replay controls.

import { motion, AnimatePresence } from "framer-motion";
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
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="glass-card p-6 space-y-6"
    >
      <h2 className="text-xl font-bold text-white tracking-wide glow-text">
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
              className="w-full text-center space-y-2"
            >
              {/* Album art placeholder */}
              <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-purple-600/40 to-cyan-500/40 border border-white/10 flex items-center justify-center text-4xl shadow-lg">
                🎶
              </div>
              <p className="text-2xl font-bold text-white mt-2">{song.title}</p>
              <p className="text-gray-400">{song.artist}</p>
              <div className="flex justify-center gap-2 flex-wrap mt-1">
                <span className="px-2 py-0.5 rounded bg-white/5 text-gray-400 text-xs">{song.genre}</span>
                <span className="px-2 py-0.5 rounded bg-white/5 text-gray-400 text-xs">{song.bpm} BPM</span>
                {song.tags.map((tag) => (
                  <span key={tag} className="px-2 py-0.5 rounded bg-neon-green/10 text-neon-green text-xs">
                    #{tag}
                  </span>
                ))}
              </div>
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
            onClick={() => onFeedback(reaction)}
            className={`flex-1 py-3 rounded-xl font-semibold text-sm transition-all ${color}`}
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
        className="w-full py-3 rounded-xl font-bold bg-gradient-to-r from-neon-green/80 to-cyan-400/80
          text-black tracking-wide shadow-[0_0_15px_#39ff1440] hover:shadow-[0_0_25px_#39ff1470]
          transition-shadow disabled:opacity-50"
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
              lastReward > 0 ? "text-neon-green" : "text-red-400"
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
