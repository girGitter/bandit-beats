// lib/api.ts — typed API client for the Bandit-Beats backend

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Algorithm = "epsilon_greedy" | "ucb";
export type Mood = "happy" | "sad" | "energetic";
export type Activity = "study" | "gym" | "relax";
export type TimeOfDay = "morning" | "evening" | "night";
export type Reaction = "listen" | "skip" | "replay";

export interface Song {
  id: string;
  title: string;
  artist: string;
  genre: string;
  bpm: number;
  tags: string[];
  album?: string;
  album_art?: string;
  spotify_id?: string;
  embed_url?: string;
  preview_url?: string;
  external_url?: string;
  duration_ms?: number;
}

export interface RecommendResponse {
  algorithm: Algorithm;
  song_id: string;
  song: Song;
  action_index: number;
}

export interface FeedbackResponse {
  song_id: string;
  reaction: Reaction;
  reward: number;
  new_q_value: number;
  action_count: number;
  total_steps: number;
  average_reward: number;
}

export interface PlotlyTrace {
  type: string;
  mode?: string;
  name?: string;
  x: number[];
  y: number[];
  line?: { color: string; width: number };
  marker?: { color: string | string[] };
}

export interface PlotlyAxisLayout {
  title: string;
  color?: string;
  gridcolor?: string;
}

export interface PlotlyLayout {
  title: string;
  xaxis: PlotlyAxisLayout;
  yaxis: PlotlyAxisLayout;
  paper_bgcolor: string;
  plot_bgcolor: string;
  font: { color: string; family: string };
  legend?: { orientation: string };
}

export interface ChartData {
  data: PlotlyTrace[];
  layout: PlotlyLayout;
}

export interface SimulateResponse {
  n_steps: number;
  reward_curve: ChartData;
  regret_curve: ChartData;
  comparison: ChartData;
  epsilon_greedy: { final_avg_reward: number; final_regret: number };
  ucb: { final_avg_reward: number; final_regret: number };
}

export interface MetricsResponse {
  reward_curve: ChartData;
  regret_curve: ChartData;
  comparison: ChartData;
  stats: Record<Algorithm, Record<string, number>>;
}

// ---- API calls ----

export async function getRecommendation(
  algorithm: Algorithm,
  mood: Mood,
  activity: Activity,
  time: TimeOfDay
): Promise<RecommendResponse> {
  const url = `${API_BASE}/recommend?algorithm=${algorithm}&mood=${mood}&activity=${activity}&time=${time}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Recommend failed: ${res.statusText}`);
  return res.json();
}

export async function sendFeedback(
  algorithm: Algorithm,
  song_id: string,
  reaction: Reaction,
  mood: Mood,
  activity: Activity,
  time: TimeOfDay
): Promise<FeedbackResponse> {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ algorithm, song_id, reaction, mood, activity, time }),
  });
  if (!res.ok) throw new Error(`Feedback failed: ${res.statusText}`);
  return res.json();
}

export async function getMetricsCharts(): Promise<MetricsResponse> {
  const res = await fetch(`${API_BASE}/metrics/charts`);
  if (!res.ok) throw new Error(`Metrics failed: ${res.statusText}`);
  return res.json();
}

export async function runSimulation(nSteps = 300): Promise<SimulateResponse> {
  const res = await fetch(`${API_BASE}/metrics/simulate?n_steps=${nSteps}`);
  if (!res.ok) throw new Error(`Simulation failed: ${res.statusText}`);
  return res.json();
}
