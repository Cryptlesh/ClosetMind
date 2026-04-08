import React, { useState } from 'react';
import { Mail, Lock, LogIn } from 'lucide-react';

const Login = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate login
    setTimeout(() => {
      if (email === 'closetmind9@gmail.com') {
        onSuccess();
      } else {
        alert('Invalid email. Please use the demo user: closetmind9@gmail.com');
      }
      setLoading(false);
    }, 800);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass w-full max-w-md p-10 rounded-2xl animate-fade-in relative overflow-hidden">
        {/* Glow effects */}
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-primary/20 blur-[80px]" />
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-secondary/10 blur-[80px]" />

        <div className="relative z-10">
          <div className="text-center mb-10">
            <h1 className="text-4xl font-extrabold tracking-tight mb-2">ClosetMind</h1>
            <p className="text-white/50 font-manrope">The Ethereal Stylist Ecosystem</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-1">
              <label className="text-xs uppercase tracking-widest font-bold text-white/40 ml-1">Email Pipeline</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30 group-focus-within:text-primary transition-smooth" size={18} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="closetmind9@gmail.com"
                  className="input-glass w-full pl-12 pr-4 py-4 rounded-xl text-white placeholder:text-white/20"
                  required
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs uppercase tracking-widest font-bold text-white/40 ml-1">Secure Core</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30 group-focus-within:text-primary transition-smooth" size={18} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input-glass w-full pl-12 pr-4 py-4 rounded-xl text-white placeholder:text-white/20"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 mt-4"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-background/30 border-t-background rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn size={20} />
                  <span>Initialize Sync</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-8 text-center">
            <a href="#" className="text-sm text-white/30 hover:text-primary transition-smooth">
              Neural Key Recovery
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
