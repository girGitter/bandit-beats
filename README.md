# 🎵 Bandit Beats

> **Context-Aware Music Recommendation System using Reinforcement Learning**

A production-quality full-stack application that recommends music based on your current context — mood, activity, and time of day — using multi-armed bandit algorithms that learn from your feedback in real time.

---

## Problem Statement

Traditional music recommenders rely on static collaborative filtering or content-based approaches that don't adapt quickly to how you feel *right now*. Bandit Beats solves this by framing music recommendation as a **reinforcement learning problem**:

- **State** → Your context (mood + activity + time of day)
- **Actions** → Songs to recommend
- **Reward** → Your feedback (play, skip, replay)

The system learns which songs work best for each context purely from interaction data — no pre-labelled training set required.

---

## How Reinforcement Learning is Used

### Multi-Armed Bandits

Imagine a row of slot machines (bandits), each with an unknown payout rate. You want to maximise total reward. The challenge: you don't know which machine is best until you try them.

In Bandit Beats:
- Each **song** is one arm of the bandit
- Pulling an arm = recommending a song
- The **reward** is +1 (listen), -1 (skip), or +2 (replay)
- The agent updates its belief about each song after every interaction

### Exploration vs Exploitation

The core dilemma in RL:
- **Exploit** — always recommend the song with the highest known reward (greedy)
- **Explore** — occasionally try other songs to discover hidden gems

Too much exploitation → stuck on a mediocre song forever  
Too much exploration → never commits to good songs

Both algorithms balance this trade-off differently.

---

## Algorithms Implemented

### ε-Greedy (`epsilon_greedy.py`)

```
With probability ε  → pick a random song    (explore)
With probability 1-ε → pick the best song   (exploit)
```

- Simple and effective
- ε decays over time: aggressive early exploration, convergence later
- Default: ε=0.15, decay=0.995, min=0.01

### UCB — Upper Confidence Bound (`ucb.py`)

```
UCB(a) = Q[a] + c × √(ln(t) / N[a])
```

- `Q[a]` = estimated mean reward for song `a`
- `t` = total steps taken
- `N[a]` = times song `a` has been tried
- `c` = exploration constant (default: 1.4)

Songs tried rarely have a large bonus → they get explored.  
Once well-sampled, the formula reduces to pure exploitation.  
UCB is theoretically optimal for the stochastic bandit problem.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│                                                                  │
│  ┌─────────────────────┐     ┌────────────────────────────────┐  │
│  │   ContextSelector   │     │       Analytics Dashboard      │  │
│  │  mood / activity /  │     │  • Avg Reward curve (Plotly)  │  │
│  │    time / algo      │     │  • Cumulative Regret curve    │  │
│  └──────────┬──────────┘     │  • Algorithm Comparison bar   │  │
│             │                └────────────────────────────────┘  │
│  ┌──────────▼──────────┐                                         │
│  │  RecommendationCard │                                         │
│  │  ▶ Play  ⏭ Skip     │                                         │
│  │  🔁 Replay          │                                         │
│  └──────────┬──────────┘                                         │
└─────────────┼────────────────────────────────────────────────────┘
              │  HTTP (REST)
              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
│                                                                  │
│  GET  /recommend   → select action via bandit agent             │
│  POST /feedback    → update Q-values with reward                │
│  GET  /metrics/charts   → Plotly chart data (live)             │
│  GET  /metrics/simulate → run full simulation, return charts    │
│  GET  /state/{algo}     → agent internal state snapshot        │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐ │
│  │  EpsilonGreedy│   │   UCBAgent   │   │    BanditAgent base  │ │
│  │  Agent        │   │              │   │  Q-values, N counts  │ │
│  └──────────────┘   └──────────────┘   └──────────────────────┘ │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐                            │
│  │  simulation  │   │   metrics    │                            │
│  │  probabilistic│   │  charts +   │                            │
│  │  user model  │   │  stats       │                            │
│  └──────────────┘   └──────────────┘                            │
└──────────────────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DATA  /data/songs.json                        │
│  10 songs with genre, BPM, tags, preferred_contexts             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Details |
|---------|---------|
| 🎛️ Context Selector | Mood (happy/sad/energetic), Activity (study/gym/relax), Time (morning/evening/night) |
| 🤖 Two RL Algorithms | ε-Greedy with decay, UCB1 with configurable exploration constant |
| ⚡ Real-time Learning | Q-values update instantly on every Play/Skip/Replay |
| 📊 Live Charts | Average reward curve, cumulative regret, algorithm comparison |
| 🤖 Simulation Mode | Run 100–1000 step simulations and compare algorithm performance |
| 🎨 Dark Neon UI | Glassmorphism cards, neon green/purple/cyan accents, Framer Motion animations |
| 🔄 Reward System | +1 listen, −1 skip, +2 replay |

---

## Screenshots

> _Run the app locally to see it in action (see How to Run below)._

The UI consists of two panels:
- **Left**: Context selector + recommendation card with Play/Skip/Replay controls
- **Right**: Analytics dashboard with Plotly charts comparing ε-Greedy vs UCB

---

## How to Run

### Prerequisites

- Python 3.11+
- Node.js 18+

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install

# Development mode
npm run dev

# Production build
npm run build && npm run start
```

The app will be available at `http://localhost:3000`.

> **Note:** The frontend connects to `http://localhost:8000` by default.  
> Override with `NEXT_PUBLIC_API_URL=http://your-backend-host` in `.env.local`.

---

## Project Structure

```
bandit-beats/
├── backend/
│   ├── main.py              # FastAPI app + all endpoints
│   ├── bandit.py            # BanditAgent base class
│   ├── epsilon_greedy.py    # ε-Greedy agent
│   ├── ucb.py               # UCB1 agent
│   ├── simulation.py        # Probabilistic user simulator
│   ├── metrics.py           # Reward/regret + Plotly chart builders
│   └── requirements.txt
├── frontend/
│   └── app/
│       ├── page.tsx             # Main dashboard page
│       ├── layout.tsx           # Root layout
│       ├── globals.css          # Dark theme + utility classes
│       ├── components/
│       │   ├── ContextSelector.tsx    # Mood/activity/time/algo picker
│       │   ├── RecommendationCard.tsx # Song display + feedback buttons
│       │   └── Dashboard.tsx          # Plotly analytics dashboard
│       └── lib/
│           └── api.ts           # Typed API client
├── data/
│   └── songs.json           # 10-song catalogue with context metadata
└── README.md
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/songs` | List all songs |
| GET | `/recommend?algorithm=&mood=&activity=&time=` | Get recommendation |
| POST | `/feedback` | Submit reaction (listen/skip/replay) |
| GET | `/state/{algorithm}` | Agent state snapshot |
| GET | `/metrics/charts` | Live Plotly chart data |
| GET | `/metrics/simulate?n_steps=300` | Run simulation + return charts |

---

## Reward System

| User Action | Reward | RL Signal |
|-------------|--------|-----------|
| ▶️ Play (listen) | +1.0 | Positive reinforcement |
| ⏭ Skip | −1.0 | Negative reinforcement |
| 🔁 Replay | +2.0 | Strong positive reinforcement |

Q-values are updated using the **incremental mean** rule:
```
Q[a] ← Q[a] + (1/N[a]) × (reward − Q[a])
```

---

## Future Improvements

- **Contextual Bandits**: Use the context vector directly in the value function (LinUCB, NeuralBandit)
- **Thompson Sampling**: Bayesian exploration via posterior sampling
- **Persistent State**: Store Q-values in Redis/PostgreSQL across sessions
- **User Profiles**: Separate agent per user, not one global agent
- **Real Music API**: Connect to Spotify/Last.fm for real track data
- **A/B Testing Framework**: Compare algorithms across real users
- **Mobile PWA**: Offline-capable progressive web app

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React, Tailwind CSS, Framer Motion, Plotly.js |
| Backend | Python, FastAPI, NumPy, Pandas, Plotly |
| RL Core | Custom multi-armed bandit implementation (no external RL library) |
| Data | Static JSON song catalogue with context-preference metadata |

---

*Built as a portfolio-quality demonstration of reinforcement learning applied to a real-world recommendation problem.*
