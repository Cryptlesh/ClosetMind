import React, { useState, useEffect } from 'react';
import { Camera, MapPin, User, ChevronRight, Upload } from 'lucide-react';
import API_BASE_URL from '../api/config';

const ProfileSetup = ({ onComplete }) => {
  const [formData, setFormData] = useState({
    name: '',
    gender: 'agnostic',
    country: 'United States',
    state: 'California',
    city: 'San Francisco'
  });
  const [imagePreview, setImagePreview] = useState(null);
  const [selfieFile, setSelfieFile] = useState(null);
  const fileInputRef = React.useRef(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/user/profile`);
        const result = await response.json();
        if (result.status === 'success' && result.data.name) {
          const d = result.data;
          setFormData({
            name: d.name,
            gender: d.gender || 'agnostic',
            country: d.country || 'United States',
            state: d.state || 'California',
            city: d.city || 'San Francisco'
          });
          if (d.selfie_url) {
            // Ensure full URL for preview
            const fullUrl = d.selfie_url.startsWith('http') 
              ? d.selfie_url 
              : `${API_BASE_URL}/${d.selfie_url}`;
            setImagePreview(fullUrl);
          }
        }
      } catch (err) {
        console.error('Failed to fetch profile pre-fill:', err);
      }
    };
    fetchProfile();
  }, []);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelfieFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name) return;
    
    const submitData = new FormData();
    submitData.append('name', formData.name);
    submitData.append('gender', formData.gender);
    submitData.append('country', formData.country);
    submitData.append('state', formData.state);
    submitData.append('city', formData.city);
    
    if (selfieFile) {
      submitData.append('selfie', selfieFile);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/user/profile`, {
        method: 'POST',
        body: submitData
      });
      const result = await response.json();
      console.log('Profile Synced:', result);
      onComplete(formData);
    } catch (err) {
      console.error('Failed to sync profile:', err);
      onComplete(formData);
    }
  };

  return (
    <div className="min-h-screen pt-32 pb-20 px-4">
      <form id="profile-form" onSubmit={handleSubmit} className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12">
        <div className="space-y-8">
          <div className="mb-10">
            <h1 className="text-5xl font-extrabold tracking-tighter mb-4">Profile Engine</h1>
            <p className="text-white/40 font-manrope text-lg">Define your identity in the ClosetMind ecosystem.</p>
          </div>

          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs uppercase tracking-widest font-bold text-white/40 ml-1">Identity</label>
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30 group-focus-within:text-primary transition-smooth" size={18} />
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="E.g. Alex"
                    className="input-glass w-full pl-12 pr-4 py-4 rounded-xl text-white placeholder:text-white/20"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs uppercase tracking-widest font-bold text-white/40 ml-1">Gender Sync</label>
                <div className="relative group">
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({...formData, gender: e.target.value})}
                    className="input-glass w-full pl-6 pr-10 py-4 rounded-xl text-white appearance-none cursor-pointer"
                  >
                    <option value="male">Masculine</option>
                    <option value="female">Feminine</option>
                    <option value="agnostic">Neutral / Fluid</option>
                  </select>
                  <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 text-white/30 rotate-90" size={18} />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs uppercase tracking-widest font-bold text-white/40 ml-1">Core Location (Weather Hook)</label>
              <div className="grid grid-cols-3 gap-4">
                <div className="relative group">
                  <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30 group-focus-within:text-primary transition-smooth" size={16} />
                  <input
                    type="text"
                    value={formData.country}
                    onChange={(e) => setFormData({...formData, country: e.target.value})}
                    placeholder="Country"
                    className="input-glass w-full pl-10 pr-4 py-4 rounded-xl text-white text-sm"
                    required
                  />
                </div>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({...formData, state: e.target.value})}
                  placeholder="State"
                  className="input-glass w-full px-4 py-4 rounded-xl text-white text-sm"
                  required
                />
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({...formData, city: e.target.value})}
                  placeholder="City"
                  className="input-glass w-full px-4 py-4 rounded-xl text-white text-sm"
                  required
                />
              </div>
            </div>

            <button type="submit" form="profile-form" className="btn-primary w-full flex items-center justify-center gap-2 group">
              <span>Finalize Core Setup</span>
              <ChevronRight className="group-hover:translate-x-1 transition-smooth" size={20} />
            </button>
          </div>
        </div>

        <div className="space-y-8">
          <div className="space-y-2">
            <label className="text-xs uppercase tracking-widest font-bold text-white/40 ml-1">AI Base Model</label>
            <div className="relative aspect-[4/5] rounded-3xl overflow-hidden glass border-2 border-white/5 group transition-smooth hover:border-primary/30">
              {imagePreview ? (
                <img src={imagePreview} className="w-full h-full object-cover" alt="Preview" />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center p-12 text-center space-y-4">
                  <div className="p-6 rounded-full bg-white/5 mb-2 group-hover:bg-primary/10 transition-smooth">
                    <Camera size={48} className="text-white/20 group-hover:text-primary transition-smooth" />
                  </div>
                  <h3 className="text-xl font-bold">Snap Your Drip</h3>
                  <p className="text-white/30 text-sm">Upload your base avatar for personalized AI try-ons.</p>
                  <button 
                    type="button"
                    onClick={() => fileInputRef.current.click()}
                    className="btn-secondary inline-block py-2 px-6 cursor-pointer"
                  >
                    Select Asset
                  </button>
                </div>
              )}
              <input 
                type="file" 
                ref={fileInputRef}
                className="hidden" 
                accept="image/*" 
                onChange={handleImageUpload} 
                id="selfie-upload" 
              />
            </div>
            {imagePreview && (
              <button 
                type="button"
                onClick={() => fileInputRef.current.click()}
                className="w-full text-center text-xs text-primary/60 hover:text-primary cursor-pointer mt-2 font-bold uppercase tracking-widest"
              >
                Change Asset
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
};

export default ProfileSetup;
