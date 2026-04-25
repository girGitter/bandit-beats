"use client";
// components/ContextSelector.tsx
// Left panel: mood, activity, time selectors + algorithm toggle

import { motion } from "framer-motion";
import type { Mood, Activity, TimeOfDay, Algorithm } from "../lib/api";

interface Props {
  mood: Mood;
  activity: Activity;
  time: TimeOfDay;
  algorithm: Algorithm;
  onMood: (v: Mood) => void;
  onActivity: (v: Activity) => void;
  onTime: (v: TimeOfDay) => void;
  onAlgorithm: (v: Algorithm) => void;
}

type Option<T> = { value: T; label: string; emoji: string };

const moods: Option<Mood>[] = [
  { value: "happy",    label: "Happy",     emoji: "😊" },
  { value: "sad",      label: "Sad",       emoji: "😔" },
  { value: "energetic",label: "Energetic", emoji: "⚡" },
];

const activities: Option<Activity>[] = [
  { value: "study", label: "Study", emoji: "📚" },
  { value: "gym",   label: "Gym",   emoji: "🏋️" },
  { value: "relax", label: "Relax", emoji: "🛋️" },
];

const times: Option<TimeOfDay>[] = [
  { value: "morning", label: "Morning", emoji: "🌅" },
  { value: "evening", label: "Evening", emoji: "🌇" },
  { value: "night",   label: "Night",   emoji: "🌙" },
];

function PillGroup<T extends string>({
  options,
  selected,
  onSelect,
}: {
  options: Option<T>[];
  selected: T;
  onSelect: (v: T) => void;
}) {
  return (
    <div className="flex gap-2 flex-wrap">
      {options.map((opt) => (
        <motion.button
          key={opt.value}
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onSelect(opt.value)}
          className={`px-4 py-2 rounded-none text-sm font-medium transition-all border
            ${
              selected === opt.value
                ? "bg-[#FF3B00] border-[#FF3B00] text-white"
                : "bg-transparent border-[#222] text-gray-400 hover:border-[#555]"
            }`}
        >
          {opt.emoji} {opt.label}
        </motion.button>
      ))}
    </div>
  );
}

export default function ContextSelector({
  mood,
  activity,
  time,
  algorithm,
  onMood,
  onActivity,
  onTime,
  onAlgorithm,
}: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-card p-6 space-y-6"
    >
      <h2 className="text-xl font-bold text-white tracking-wide glow-text">
        🎛️ Your Context
      </h2>

      {/* Mood */}
      <div className="space-y-2">
        <label className="text-xs text-gray-400 uppercase tracking-widest">Mood</label>
        <PillGroup options={moods} selected={mood} onSelect={onMood} />
      </div>

      {/* Activity */}
      <div className="space-y-2">
        <label className="text-xs text-gray-400 uppercase tracking-widest">Activity</label>
        <PillGroup options={activities} selected={activity} onSelect={onActivity} />
      </div>

      {/* Time */}
      <div className="space-y-2">
        <label className="text-xs text-gray-400 uppercase tracking-widest">Time of Day</label>
        <PillGroup options={times} selected={time} onSelect={onTime} />
      </div>

      {/* Algorithm */}
      <div className="space-y-2">
        <label className="text-xs text-gray-400 uppercase tracking-widest">Algorithm</label>
        <div className="flex gap-3">
          {(["epsilon_greedy", "ucb"] as Algorithm[]).map((alg) => (
            <motion.button
              key={alg}
              whileHover={{ scale: 1.06 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onAlgorithm(alg)}
              className={`flex-1 py-2 rounded-none text-sm font-semibold transition-all border
                ${
                  algorithm === alg
                    ? "bg-[#1D00FF] border-[#1D00FF] text-white"
                    : "bg-transparent border-[#222] text-gray-400 hover:border-[#555]"
                }`}
            >
              {alg === "epsilon_greedy" ? "ε-Greedy" : "UCB"}
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
