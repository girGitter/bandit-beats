"use client";
/**
 * page.tsx — Main dashboard for Bandit-Beats.
 *
 * Layout:
 *   - Header (title + tagline)
 *   - Left column: ContextSelector + RecommendationCard
 *   - Right column: Analytics Dashboard
 */

import { useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import ContextSelector from "./components/ContextSelector";
import RecommendationCard from "./components/RecommendationCard";
import Dashboard from "./components/Dashboard";
import {
  getRecommendation,
  sendFeedback,
} from "./lib/api";
import type {
  Algorithm,
  Mood,
  Activity,
  TimeOfDay,
  Reaction,
  Song,
} from "./lib/api";

export default function Home() {
  // Context state
  const [mood, setMood]         = useState<Mood>("happy");
  const [activity, setActivity] = useState<Activity>("study");
  const [time, setTime]         = useState<TimeOfDay>("morning");
  const [algorithm, setAlgorithm] = useState<Algorithm>("epsilon_greedy");

  // Recommendation state
  const [song, setSong]             = useState<Song | null>(null);
  const [loading, setLoading]       = useState(false);
  const [lastReward, setLastReward] = useState<number | null>(null);
  const [totalSteps, setTotalSteps] = useState(0);
  const [avgReward, setAvgReward]   = useState(0);

  // Trigger dashboard refresh after feedback
  const [refreshTick, setRefreshTick] = useState(0);

  // Track the current song_id for feedback
  const currentSongId = useRef<string | null>(null);

  const handleRecommend = useCallback(async () => {
    setLoading(true);
    setLastReward(null);
    try {
      const res = await getRecommendation(algorithm, mood, activity, time);
      setSong(res.song);
      currentSongId.current = res.song_id;
    } catch (err) {
      console.error("Recommendation error:", err);
    } finally {
      setLoading(false);
    }
  }, [algorithm, mood, activity, time]);

  const handleFeedback = useCallback(
    async (reaction: Reaction) => {
      if (!currentSongId.current) return;
      try {
        const res = await sendFeedback(
          algorithm,
          currentSongId.current,
          reaction,
          mood,
          activity,
          time
        );
        setLastReward(res.reward);
        setTotalSteps(res.total_steps);
        setAvgReward(res.average_reward);
        setRefreshTick((t) => t + 1);
      } catch (err) {
        console.error("Feedback error:", err);
      }
    },
    [algorithm, mood, activity, time]
  );

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="px-6 pt-8 pb-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight uppercase">
            <span className="text-[#FF3B00]">Bandit</span>
            <span className="text-white"> Beats.</span>
          </h1>
          <p className="mt-2 text-gray-400 text-sm md:text-base max-w-xl mx-auto uppercase tracking-widest text-xs mt-4">
            Context-aware music recommendations powered by{" "}
            <span className="text-[#1D00FF] font-semibold">multi-armed bandit</span>{" "}
            reinforcement learning
          </p>
        </motion.div>
      </header>

      {/* Main grid */}
      <main className="flex-1 px-4 pb-10 pt-4 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* Left column */}
          <div className="flex flex-col gap-6">
            <ContextSelector
              mood={mood}
              activity={activity}
              time={time}
              algorithm={algorithm}
              onMood={setMood}
              onActivity={setActivity}
              onTime={setTime}
              onAlgorithm={setAlgorithm}
            />
            <RecommendationCard
              song={song}
              loading={loading}
              lastReward={lastReward}
              totalSteps={totalSteps}
              avgReward={avgReward}
              onRecommend={handleRecommend}
              onFeedback={handleFeedback}
            />
          </div>

          {/* Right column */}
          <Dashboard refreshTrigger={refreshTick} />
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-gray-600">
        Bandit-Beats · ε-Greedy &amp; UCB · Built with FastAPI + Next.js
      </footer>
    </div>
  );
}
