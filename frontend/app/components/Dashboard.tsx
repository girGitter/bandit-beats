"use client";
// components/Dashboard.tsx
// Visualization dashboard: reward curve, regret curve, algorithm comparison.

import { useEffect, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { runSimulation, getMetricsCharts } from "../lib/api";
import type { ChartData, SimulateResponse } from "../lib/api";

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface TabCharts {
  reward_curve: ChartData;
  regret_curve: ChartData;
  comparison: ChartData;
}

type Tab = "reward" | "regret" | "compare";

const TABS: { id: Tab; label: string }[] = [
  { id: "reward",  label: "📈 Avg Reward" },
  { id: "regret",  label: "📉 Regret" },
  { id: "compare", label: "🏆 Compare" },
];

const plotConfig = { responsive: true, displayModeBar: false };
const baseLayout = {
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { color: "#e0e0e0", family: "Inter, sans-serif", size: 12 },
  margin: { t: 40, l: 50, r: 20, b: 50 },
  legend: { orientation: "h" as const },
};

export default function Dashboard({ refreshTrigger }: { refreshTrigger: number }) {
  const [charts, setCharts] = useState<TabCharts | null>(null);
  const [simResult, setSimResult] = useState<SimulateResponse | null>(null);
  const [tab, setTab] = useState<Tab>("reward");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"live" | "sim">("sim");
  const [nSteps, setNSteps] = useState(300);

  const loadLiveCharts = useCallback(async () => {
    try {
      const data = await getMetricsCharts();
      setCharts({
        reward_curve: data.reward_curve,
        regret_curve: data.regret_curve,
        comparison:   data.comparison,
      });
    } catch {
      // silently ignore — no data yet
    }
  }, []);

  const loadSimulation = useCallback(async () => {
    setLoading(true);
    try {
      const data = await runSimulation(nSteps);
      setSimResult(data);
      setCharts({
        reward_curve: data.reward_curve,
        regret_curve: data.regret_curve,
        comparison:   data.comparison,
      });
    } finally {
      setLoading(false);
    }
  }, [nSteps]);

  // Refresh live charts when feedback is sent
  useEffect(() => {
    if (mode === "live") {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      loadLiveCharts();
    }
  }, [refreshTrigger, mode, loadLiveCharts]);

  // Load simulation on mount
  useEffect(() => {
    if (mode === "sim") {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      loadSimulation();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  const activeChart = charts
    ? tab === "reward"
      ? charts.reward_curve
      : tab === "regret"
      ? charts.regret_curve
      : charts.comparison
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="glass-card p-6 space-y-5 h-full"
    >
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-xl font-bold text-white tracking-wide uppercase">
          📊 Analytics Dashboard
        </h2>

        {/* Mode toggle */}
        <div className="flex gap-2 text-sm">
          {(["sim", "live"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`px-3 py-1 rounded-none border transition-all ${
                mode === m
                  ? "bg-[#1D00FF] border-[#1D00FF] text-white"
                  : "bg-transparent border-[#222] text-gray-500 hover:border-[#555]"
              }`}
            >
              {m === "sim" ? "🤖 Simulation" : "⚡ Live"}
            </button>
          ))}
        </div>
      </div>

      {/* Simulation controls */}
      {mode === "sim" && (
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-400">Steps:</label>
            <select
              value={nSteps}
              onChange={(e) => setNSteps(Number(e.target.value))}
              className="bg-transparent border border-[#333] rounded-none px-2 py-1 text-sm text-white"
            >
              {[100, 200, 300, 500, 1000].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={loadSimulation}
            disabled={loading}
            className="px-4 py-1.5 rounded-none text-sm font-semibold border border-[#FF3B00] text-[#FF3B00] hover:bg-[#FF3B00] hover:text-white transition-all disabled:opacity-50 uppercase tracking-wider"
          >
            {loading ? "Running…" : "▶ Run Simulation"}
          </motion.button>
          {simResult && (
            <div className="flex gap-4 text-xs text-gray-400 mt-2">
              <span>
                ε-Greedy avg: <span className="text-[#FF3B00] font-bold">{simResult.epsilon_greedy.final_avg_reward.toFixed(3)}</span>
              </span>
              <span>
                UCB avg: <span className="text-[#1D00FF] font-bold">{simResult.ucb.final_avg_reward.toFixed(3)}</span>
              </span>
            </div>
          )}
        </div>
      )}

      {/* Tab bar */}
      <div className="flex gap-2 border-b border-white/5 pb-1">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-1.5 text-sm rounded-none transition-all ${
              tab === t.id
                ? "text-[#FF3B00] border-b-2 border-[#FF3B00]"
                : "text-gray-500 hover:text-gray-300 border-b-2 border-transparent"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="relative min-h-[320px]">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center z-10">
            <div className="w-10 h-10 border-2 border-[#1D00FF] border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        {activeChart ? (
          <Plot
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            data={activeChart.data as any[]}
            layout={{
              ...activeChart.layout,
              ...baseLayout,
              xaxis: { ...(activeChart.layout.xaxis as object), gridcolor: "#1f1f1f" },
              yaxis: { ...(activeChart.layout.yaxis as object), gridcolor: "#1f1f1f" },
            } as object}
            config={plotConfig}
            style={{ width: "100%", height: "100%" }}
            className="min-h-[320px]"
          />
        ) : (
          !loading && (
            <div className="flex items-center justify-center h-[320px] text-gray-500 text-sm">
              {mode === "live"
                ? "Interact with the recommender to generate data."
                : "Click ▶ Run Simulation to generate charts."}
            </div>
          )
        )}
      </div>

      {/* Legend explainer */}
      <div className="flex gap-4 text-xs text-gray-500 justify-center flex-wrap pt-1">
        <span className="flex items-center gap-1.5">
          <span className="w-4 h-1 rounded-none bg-[#FF3B00] inline-block" /> ε-Greedy
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-4 h-1 rounded-none bg-[#1D00FF] inline-block" /> UCB
        </span>
      </div>
    </motion.div>
  );
}
