import React, { useState } from 'react';
import { CheckCircle2, Circle, ChevronDown, ChevronUp } from 'lucide-react';

interface Task {
  text: string;
  completed: boolean;
}

interface Section {
  title: string;
  description: string;
  tasks: Task[];
  expanded: boolean;
}

export default function ProjectTracker() {
  const [sections, setSections] = useState<Section[]>([
    {
      title: "🧱 CORE MODULES SETUP",
      description: "Essential trading functionality and core features",
      expanded: true,
      tasks: [
        { text: "Capital.com Live/Demo support (API, login, account scan)", completed: false },
        { text: "TP1–TP5 trade logic", completed: false },
        { text: "SL / Breakeven / Trailing SL engine", completed: false },
        { text: "Multi-timeframe confirmation (1m–4H)", completed: false },
        { text: "Risk % per trade based on capital", completed: false },
        { text: "Candle pattern recognition (Doji, Engulfing, etc.)", completed: false },
        { text: "Telegram trade alerts (dual language support)", completed: false },
        { text: "Strategy modes (Safe / Balanced / Aggressive)", completed: false },
        { text: "Indicator stack (EMA, MACD, ATR, BB, RSI, VWAP)", completed: false },
        { text: "Liquidity / Spread / Volume filters", completed: false },
        { text: "Signal formatter (MT5 + Capital)", completed: false },
        { text: "send_signal_with_commentary() format engine", completed: false },
        { text: "News monitor (Arabic + English with RSS)", completed: false }
      ]
    },
    {
      title: "📊 DASHBOARD & LOGGING",
      description: "Monitoring and visualization features",
      expanded: false,
      tasks: [
        { text: "Capital Tracker: Balance scan, equity log (CSV)", completed: false },
        { text: "Equity Curve Chart", completed: false },
        { text: "Capital Growth progress bar (333 → 1500 AED)", completed: false },
        { text: "AI Insights Panel (Smart Score / Drawdown)", completed: false },
        { text: "Bot Uptime + Status Monitor", completed: false },
        { text: "Flask HTML + Chart.js UI", completed: false },
        { text: "VPS ping / offline detection", completed: false },
        { text: "Restart / Pause button from dashboard", completed: false },
        { text: "Telegram alerts: bot crashed / restarted / sleep", completed: false },
        { text: "TradingView Webhook Integration", completed: false }
      ]
    },
    {
      title: "🧠 AI & SMART SYSTEMS",
      description: "Advanced AI and machine learning features",
      expanded: false,
      tasks: [
        { text: "GPT trade learning engine", completed: false },
        { text: "Signal confidence scoring (news/volume/FVG)", completed: false },
        { text: "News-based trade reversal detection", completed: false },
        { text: "Adaptive strategy AI: learns winning sessions", completed: false },
        { text: "Pine Script auto-parser + Webhook", completed: false },
        { text: "Telegram reason & confidence tag", completed: false },
        { text: "Pre-news filter alerts", completed: false },
        { text: "Capital growth predictor", completed: false },
        { text: "Time window controller (8AM–5PM only)", completed: false },
        { text: "Auto-recovery trades after SL", completed: false }
      ]
    },
    {
      title: "🧪 TESTING & SIGNAL PIPELINE",
      description: "Testing infrastructure and signal management",
      expanded: false,
      tasks: [
        { text: "CLI test command: --test-signal", completed: false },
        { text: "Signal Recap Engine (TP hit, SL hit, Hold)", completed: false },
        { text: "Pre-signal Telegram alert", completed: false },
        { text: "Arabic + English commentary", completed: false },
        { text: "Trade Style tag (Scalping M15, Swing H4, etc.)", completed: false },
        { text: "PIP Summary Generator (Daily/Weekly)", completed: false },
        { text: "Visual Polish (icons, emojis, formatting)", completed: false }
      ]
    },
    {
      title: "📁 FILE MANAGEMENT & DEPLOYMENT",
      description: "Project organization and deployment",
      expanded: false,
      tasks: [
        { text: "Folder structure verified", completed: false },
        { text: "Import fix and duplication cleanup", completed: false },
        { text: "extensions.py plugin engine", completed: false },
        { text: "Deployment: Render / Gunicorn + HTTPS", completed: false },
        { text: ".env check", completed: false },
        { text: "Full export package (.py, .txt, .html)", completed: false },
        { text: "ZIP + GitHub cleaned push (optional)", completed: false }
      ]
    }
  ]);

  const toggleTask = (sectionIndex: number, taskIndex: number) => {
    setSections(sections.map((section, i) => {
      if (i === sectionIndex) {
        const newTasks = [...section.tasks];
        newTasks[taskIndex] = {
          ...newTasks[taskIndex],
          completed: !newTasks[taskIndex].completed
        };
        return { ...section, tasks: newTasks };
      }
      return section;
    }));
  };

  const toggleSection = (sectionIndex: number) => {
    setSections(sections.map((section, i) => {
      if (i === sectionIndex) {
        return { ...section, expanded: !section.expanded };
      }
      return section;
    }));
  };

  const calculateProgress = (tasks: Task[]) => {
    const completed = tasks.filter(task => task.completed).length;
    return Math.round((completed / tasks.length) * 100);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Project Tracker</h2>
        <p className="text-gray-600">MAGUS PRIME X Development Progress</p>
      </div>

      <div className="space-y-6">
        {sections.map((section, sectionIndex) => (
          <div key={section.title} className="border rounded-lg overflow-hidden">
            <div 
              className="bg-gray-50 p-4 flex items-center justify-between cursor-pointer"
              onClick={() => toggleSection(sectionIndex)}
            >
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
                <p className="text-sm text-gray-600">{section.description}</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-sm font-medium text-gray-600">
                  {calculateProgress(section.tasks)}% Complete
                </div>
                {section.expanded ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                )}
              </div>
            </div>

            {section.expanded && (
              <div className="p-4 space-y-3">
                {section.tasks.map((task, taskIndex) => (
                  <div 
                    key={taskIndex}
                    className="flex items-start space-x-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
                    onClick={() => toggleTask(sectionIndex, taskIndex)}
                  >
                    {task.completed ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                    ) : (
                      <Circle className="h-5 w-5 text-gray-300 flex-shrink-0 mt-0.5" />
                    )}
                    <span className={`text-sm ${task.completed ? 'text-gray-500 line-through' : 'text-gray-700'}`}>
                      {task.text}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}