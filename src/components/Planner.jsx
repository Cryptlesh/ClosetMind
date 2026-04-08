import React, { useState } from 'react';
import { Calendar, Send, Sparkles, ChevronRight, PlaneTakeoff, MapPin, CheckCircle2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import API_BASE_URL from '../api/config';

const Planner = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null); // 'loading', 'success', 'error'
  const [results, setResults] = useState(null);

  const handleTripSubmit = async (e) => {
    e.preventDefault();
    if (!input) return;
    
    setLoading(true);
    setSyncStatus('loading');
    setResults(null);

    try {
      const resp = await fetch(`${API_BASE_URL}/api/v1/agents/plan-outfits`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input, user_id: 'user_123' })
      });
      const result = await resp.json();
      
      const calendarLog = result.data?.weather_context || '';
      if (calendarLog.includes('[CALENDAR SYNC RESULTS]')) {
         setSyncStatus('success');
         setResults(calendarLog.split('[CALENDAR SYNC RESULTS]')[1].trim());
      } else {
         setSyncStatus('error');
         setResults('Protocol initiated, but calendar sync logs were not captured. Please check your Google Calendar directly.');
      }
    } catch (err) {
      console.error(err);
      setSyncStatus('error');
      setResults('Failed to connect to the Stylist Orchestrator.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen pt-32 pb-20 px-4 max-w-5xl mx-auto flex flex-col items-center">
      <div className="text-center space-y-4 mb-16">
        <h1 className="text-6xl font-extrabold tracking-tighter">Trip Planner</h1>
        <p className="text-white/40 font-manrope text-xl max-w-2xl">
          Where are we headed? Define your mission parameters to sync outfits directly to your Google Workspace.
        </p>
      </div>

      <div className="w-full max-w-3xl">
        <div className="glass rounded-[3rem] p-8 border-primary/20 shadow-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-smooth">
            <PlaneTakeoff size={120} />
          </div>
          
          <form onSubmit={handleTripSubmit} className="space-y-8 relative z-10">
            <div className="space-y-4">
              <label className="text-[10px] uppercase tracking-[0.2em] font-black text-primary/60 ml-2">Mission Parameters</label>
              <div className="relative group/input">
                <MapPin className="absolute left-6 top-1/2 -translate-y-1/2 text-primary/40 group-focus-within/input:text-primary transition-smooth" size={24} />
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={loading}
                  placeholder="e.g. Create a 5 day plan for Goa trip from May 1st..."
                  className="w-full bg-white/5 border border-white/10 rounded-[2rem] py-8 pl-18 pr-8 text-xl text-white placeholder:text-white/10 focus:outline-none focus:border-primary/40 focus:bg-white/10 transition-smooth shadow-inner disabled:opacity-50"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-6 rounded-2xl flex items-center justify-center gap-4 text-lg group/btn shadow-[0_20px_50px_rgba(0,196,204,0.15)] hover:shadow-[0_20px_50px_rgba(0,196,204,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-6 h-6 border-2 border-background/20 border-t-background rounded-full animate-spin" />
              ) : (
                <Sparkles size={24} className="group-hover/btn:rotate-12 transition-smooth" />
              )}
              <span className="font-black">{loading ? 'Orchestrating Sync...' : 'Generate packing protocol'}</span>
              {!loading && <ChevronRight size={24} className="group-hover/btn:translate-x-1 transition-smooth" />}
            </button>
          </form>
        </div>

        {/* Dynamic Status / Response Area */}
        <AnimatePresence>
          {syncStatus && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`mt-8 glass rounded-3xl p-8 border-2 ${
                syncStatus === 'success' ? 'border-primary/20 bg-primary/5' : 
                syncStatus === 'error' ? 'border-red-500/20 bg-red-500/5' : 
                'border-secondary/20 bg-secondary/5'
              }`}
            >
               <div className="flex items-start gap-4">
                  {syncStatus === 'success' && <CheckCircle2 className="text-primary shrink-0" size={24} />}
                  {syncStatus === 'error' && <AlertCircle className="text-red-400 shrink-0" size={24} />}
                  {syncStatus === 'loading' && <Sparkles className="text-secondary animate-pulse shrink-0" size={24} />}
                  
                  <div className="space-y-4 w-full">
                    <h3 className="text-lg font-bold">
                      {syncStatus === 'success' && 'Sync Complete'}
                      {syncStatus === 'error' && 'Execution Warning'}
                      {syncStatus === 'loading' && 'Initializing Google Workspace MCP...'}
                    </h3>
                    <p className="text-sm text-white/50 font-manrope whitespace-pre-wrap leading-relaxed">
                      {syncStatus === 'loading' ? 'Gemini is parsing your trip duration and establishing a secure stdio stream to the Calendar MCP server.' : results}
                    </p>
                    
                    {syncStatus === 'success' && (
                      <button 
                        onClick={() => window.open('https://calendar.google.com/calendar/r', '_blank')}
                        className="text-xs font-black uppercase tracking-widest text-primary flex items-center gap-2 hover:gap-3 transition-smooth"
                      >
                         Open Google Calendar <ExternalLink size={14} />
                      </button>
                    )}
                  </div>
               </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 opacity-40 grayscale group-hover:grayscale-0 transition-smooth">
           <div className="glass p-6 rounded-3xl border-white/5 flex flex-col gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-primary">
                 <Calendar size={20} />
              </div>
              <p className="text-xs font-bold uppercase tracking-widest text-white/60">Schedule Sync</p>
              <p className="text-[10px] text-white/30 font-manrope leading-relaxed">Automatically map outfits to your flight and stay durations.</p>
           </div>
           <div className="glass p-6 rounded-3xl border-white/5 flex flex-col gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-secondary">
                 <Sparkles size={20} />
              </div>
              <p className="text-xs font-bold uppercase tracking-widest text-white/60">Weather Guard</p>
              <p className="text-[10px] text-white/30 font-manrope leading-relaxed">Dynamic wardrobe selection based on destination climate data.</p>
           </div>
           <div className="glass p-6 rounded-3xl border-white/5 flex flex-col gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-white">
                 <PlaneTakeoff size={20} />
              </div>
              <p className="text-xs font-bold uppercase tracking-widest text-white/60">Bag Logic</p>
              <p className="text-[10px] text-white/30 font-manrope leading-relaxed">Optimized layering suggestions to maximize luggage space.</p>
           </div>
        </div>
      </div>
    </div>
  );
};

// Simple ExternalLink icon replacement
const ExternalLink = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
);

export default Planner;
