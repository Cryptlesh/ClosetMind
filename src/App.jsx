import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Login from './components/Login';
import ProfileSetup from './components/ProfileSetup';
import Planner from './components/Planner';
import FitVault from './components/FitVault';
import FitGenie from './components/FitGenie';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeView, setActiveView] = useState('login');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [userProfile, setUserProfile] = useState(null);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setActiveView('profile');
  };

  const handleProfileComplete = (data) => {
    setUserProfile(data);
    setActiveView('planner');
  };

  const handlePlanFit = (event) => {
    setSelectedEvent(event);
    setActiveView('genie');
  };

  // View mapping
  const renderView = () => {
    switch (activeView) {
      case 'login':
        return <Login onSuccess={handleLoginSuccess} />;
      case 'profile':
        return <ProfileSetup onComplete={handleProfileComplete} />;
      case 'planner':
        return <Planner onPlanFit={handlePlanFit} />;
      case 'vault':
        return <FitVault />;
      case 'genie':
        return <FitGenie selectedEvent={selectedEvent} />;
      default:
        return <Login onSuccess={handleLoginSuccess} />;
    }
  };

  return (
    <div className="min-h-screen bg-background text-white selection:bg-primary/30 selection:text-primary">
      {isLoggedIn && (
        <Navbar activeView={activeView} setActiveView={setActiveView} />
      )}

      <main className="relative z-0">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeView}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            {renderView()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Global Background Elements */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/10 blur-[120px] rounded-full animate-pulse delay-700" />
      </div>
    </div>
  );
}

export default App;
