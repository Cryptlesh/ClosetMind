import React, { useState } from 'react';
import { Send, MapPin, Calendar, ExternalLink, Sparkles, Wind, Sun, Shirt, Info, Trash2, User } from 'lucide-react';
import { motion } from 'framer-motion';
import API_BASE_URL from '../api/config';

const FitGenie = ({ selectedEvent }) => {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "What are we dressing for today?" }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [planData, setPlanData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input) return;
    
    setMessages(prev => [...prev, {role: 'user', text: input}]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      const resp = await fetch(`${API_BASE_URL}/api/v1/agents/plan-outfits`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: currentInput, user_id: 'user_123', is_planner: false })
      });
      const result = await resp.json();
      
      setPlanData(result.data);
      setMessages(prev => [...prev, {role: 'assistant', text: 'I have orchestrated your outfit!'}]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {role: 'assistant', text: 'Error connecting to the AI Agent.'}]);
    } finally {
      setLoading(false);
    }
  };

  const recipes = planData?.stylist_outfits?.slice(0, 1).map((outfit) => {
    // Resolve relative URLs to absolute URLs using API_BASE_URL
    let imageUrl = null;
    if (planData.vton_result) {
      imageUrl = planData.vton_result.startsWith('http') 
        ? planData.vton_result 
        : `${API_BASE_URL}/${planData.vton_result}`;
    }
    
    return {
      id: 1,
      name: `Generated Look`,
      image: imageUrl,
      breakdown: outfit.items || []
    };
  }) || [];

  return (
    <div className="min-h-screen pt-32 pb-40 px-4 max-w-7xl mx-auto flex flex-col gap-12">
      
      {/* Prompt Section: Top Entry Point */}
      <div className="w-full max-w-4xl mx-auto">
        <div className="glass rounded-3xl p-4 flex flex-col gap-4 border-white/10 shadow-2xl">
          <div className="max-h-32 overflow-y-auto px-4 space-y-4">
             {messages.map((m, i) => (
               <div key={i} className="flex gap-4 items-start animate-fade-in">
                 <div className="w-6 h-6 rounded-lg bg-primary/20 flex items-center justify-center text-[10px] text-primary font-black shrink-0">AI</div>
                 <p className="text-sm text-white/60 font-manrope leading-relaxed">{m.text}</p>
               </div>
             ))}
          </div>
          <form className="relative flex items-center" onSubmit={handleSubmit}>
            <Sparkles className="absolute left-6 text-primary hover:scale-110 transition-smooth cursor-pointer" size={20} />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask the Genie: 'Suggest me casual outfit for today' ..."
              className="w-full bg-white/5 border border-white/10 rounded-2xl py-5 pl-16 pr-20 text-white placeholder:text-white/20 focus:outline-none focus:border-primary/40 focus:bg-white/10 transition-smooth"
            />
            <div className="absolute right-4 flex items-center gap-2">
                 {loading ? (
                    <div className="p-3">
                       <div className="w-5 h-5 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
                    </div>
                 ) : (
                    <button type="submit" className="p-3 rounded-xl bg-primary text-background hover:scale-105 active:scale-95 transition-smooth">
                       <Send size={18} />
                    </button>
                 )}
            </div>
          </form>
        </div>
      </div>

      {/* Results Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
        {/* Results UI: Fit Recipe (Only 1) */}
        <div className="glass rounded-3xl overflow-hidden group hover:border-primary/40 transition-smooth flex flex-col min-h-[500px]">
          <div className="aspect-[3/4] relative overflow-hidden bg-white/5 flex items-center justify-center">
            {recipes.length > 0 && recipes[0].image ? (
              <img src={recipes[0].image} className="w-full h-full object-cover group-hover:scale-105 transition-smooth" alt="AI Try-On" />
            ) : (
              <div className="flex flex-col items-center justify-center text-white/10 p-12 text-center space-y-4">
                 <User size={120} strokeWidth={0.5} className="opacity-20 translate-y-4" />
                 <p className="text-xs font-black uppercase tracking-widest opacity-30 mt-8">Awaiting Generation Protocol</p>
              </div>
            )}
            
            {recipes.length > 0 && recipes[0].image && (
              <div className="absolute top-6 left-6 flex flex-col gap-2">
                 <span className="px-4 py-2 rounded-xl glass text-[10px] font-black uppercase tracking-widest text-primary border-primary/20 animate-fade-in">AI Try-On Model</span>
                 <span className="px-4 py-2 rounded-xl glass text-[10px] font-black uppercase tracking-widest text-secondary border-secondary/20 animate-fade-in">98% Match</span>
              </div>
            )}
          </div>
          
          {recipes.length > 0 && (
            <div className="p-8 space-y-6 flex-grow animate-fade-in">
               <h3 className="text-2xl font-extrabold tracking-tight">{recipes[0].name}</h3>
               <div className="space-y-4">
                 <h4 className="text-[10px] uppercase font-bold text-white/30 tracking-widest">Vault Assets</h4>
                 <div className="flex flex-wrap gap-3">
                   {recipes[0].breakdown.map((item, i) => (
                     // Only render if image exists and is not a default unsplash placeholder
                     (item && !item.includes('unsplash')) && (
                       <div key={i} className="w-16 h-16 rounded-xl overflow-hidden border border-white/10 glass p-1 group/thumb">
                         <img src={item.startsWith('http') ? item : `${API_BASE_URL}/${item}`} alt="Vault Item" className="w-full h-full object-cover rounded-lg group-hover/thumb:scale-110 transition-smooth" />
                       </div>
                     )
                   ))}
                 </div>
               </div>
               <button className="btn-secondary w-full hover:bg-secondary/10 hover:text-secondary group/btn">
                  Select This Fit
               </button>
            </div>
          )}
        </div>

        {/* Tips Card (Right) */}
        <div className="glass rounded-3xl p-8 relative overflow-hidden group border-secondary/20">
          <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-secondary/10 blur-3xl group-hover:bg-secondary/20 transition-smooth" />
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 rounded-xl bg-secondary/20 text-secondary border border-secondary/30">
               <Info size={24} />
            </div>
            <h2 className="text-2xl font-extrabold tracking-tight">Style & Weather Tips</h2>
          </div>
          <div className="space-y-6">
            <div className="flex items-start gap-4 p-4 rounded-2xl bg-white/5 border border-white/10">
              <Sun size={24} className="text-orange-400 mt-1" />
              <div className="space-y-1">
                 <p className="font-bold text-white/90">Weather Forecast</p>
                 <p className="text-xs text-white/40 leading-relaxed whitespace-pre-wrap">{planData?.weather_context || 'Prioritize breathable linens.'}</p>
              </div>
            </div>
            <div className="flex items-start gap-4 p-4 rounded-2xl bg-white/5 border border-white/10">
              <Shirt size={24} className="text-primary mt-1" />
              <div className="space-y-1">
                 <p className="font-bold text-white/90">Stylist Agent Tips</p>
                 <p className="text-xs text-white/40 leading-relaxed">{planData?.style_tips || 'Awaiting prompt orchestration...'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FitGenie;
