import React, { useState, useEffect } from 'react';
import { Upload, Plus, Filter, LayoutGrid, List } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import API_BASE_URL from '../api/config';

const FitVault = () => {
  const [items, setItems] = useState([]);
  const [uploading, setUploading] = useState([]);

  useEffect(() => {
    const fetchWardrobe = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/wardrobe/`);
        const result = await response.json();
        if (result.status === 'success' && result.data && result.data.length > 0) {
          const fetchedItems = result.data.map(item => {
            const url = item.image.startsWith('http') ? item.image : `${API_BASE_URL}/${item.image}`;
            
            // Build tags combining category, color, material, and standard tags
            const t = [];
            if (item.category && item.category !== 'Unknown') t.push(item.category);
            if (item.color && item.color !== 'Unknown') t.push(item.color);
            if (item.material && item.material !== 'Unknown') t.push(item.material);
            if (item.tags && Array.isArray(item.tags)) t.push(...item.tags);
            
            // Deduplicate tags
            const uniqueTags = [...new Set(t)];

            return {
              id: item.id,
              image: url,
              tags: uniqueTags.length > 0 ? uniqueTags : ['AI Processed', 'New'],
              ready: true
            };
          });
          setItems(fetchedItems);
        }
      } catch (err) {
        console.error('Error fetching wardrobe items:', err);
      }
    };
    fetchWardrobe();
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
  };

  const processFiles = async (files) => {
    const newUploads = files.map((file, index) => ({
      id: Date.now() + index,
      preview: URL.createObjectURL(file),
      loading: true
    }));
    
    setUploading([...uploading, ...newUploads]);

    const formData = new FormData();
    files.forEach(f => formData.append('files', f));

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/wardrobe/upload`, {
        method: 'POST',
        body: formData
      });
      const result = await response.json();
      
      setUploading(prev => prev.filter(item => !newUploads.find(u => u.id === item.id)));
      
      const processedItems = newUploads.map((upload, idx) => {
        const resData = result.data[idx];
        const t = [];
        if (resData) {
          if (resData.category && resData.category !== 'Unknown') t.push(resData.category);
          if (resData.color && resData.color !== 'Unknown') t.push(resData.color);
          if (resData.material && resData.material !== 'Unknown') t.push(resData.material);
          if (resData.tags && Array.isArray(resData.tags)) t.push(...resData.tags);
        }
        const uniqueTags = [...new Set(t)];

        return {
          id: upload.id,
          image: upload.preview,
          tags: uniqueTags.length > 0 ? uniqueTags : ['AI Processed', 'New'],
          ready: true
        };
      });
      
      setItems(prev => [...processedItems, ...prev]);
    } catch (err) {
      console.error('Error uploading:', err);
      // Fallback
      setUploading(prev => prev.filter(item => !newUploads.find(u => u.id === item.id)));
      setItems(prev => [...newUploads.map(u => ({...u, tags: ['Failed']})), ...prev]);
    }
  };

  return (
    <div className="min-h-screen pt-32 pb-20 px-4 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-12">
        <div className="space-y-2">
          <h1 className="text-5xl font-extrabold tracking-tighter">Fit Vault</h1>
          <p className="text-white/40 font-manrope text-lg">Your synchronized neural wardrobe repository.</p>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-3 rounded-xl glass hover:bg-white/5 transition-smooth"><Filter size={20} /></button>
          <div className="flex bg-white/5 p-1 rounded-xl border border-white/10">
            <button className="p-2 rounded-lg bg-primary text-background"><LayoutGrid size={20} /></button>
            <button className="p-2 rounded-lg text-white/40"><List size={20} /></button>
          </div>
        </div>
      </div>

      {/* Multi-upload dropzone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className="mb-12 border-2 border-dashed border-white/10 bg-white/5 rounded-3xl p-12 text-center transition-smooth group cursor-pointer hover:border-primary/50 hover:bg-white/10"
      >
        <div className="max-w-md mx-auto space-y-6">
          <div className="w-20 h-20 bg-white/5 rounded-2xl mx-auto flex items-center justify-center border border-white/10 group-hover:bg-primary/20 transition-smooth">
            <Upload size={32} className="text-white/30 group-hover:text-primary transition-smooth" />
          </div>
          <div className="space-y-2">
            <h3 className="text-2xl font-bold">Digest New Assets</h3>
            <p className="text-white/40 font-manrope">Drop multiple high-res captures to sync your physical wardrobe with the AI cloud.</p>
          </div>
          <label className="cursor-pointer inline-block">
            <span className="btn-primary">Initialize Ingest</span>
            <input type="file" multiple className="hidden" onChange={(e) => processFiles(Array.from(e.target.files))} />
          </label>
        </div>
      </div>

      {/* Wardrobe Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
        <AnimatePresence>
          {uploading.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="aspect-[3/4] rounded-3xl overflow-hidden glass border border-white/10 relative"
            >
              <img src={item.preview} className="w-full h-full object-cover opacity-30 grayscale" alt="Loading" />
              <div className="absolute inset-0 flex flex-col items-center justify-center p-8 space-y-4">
                <div className="w-12 h-12 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
                <p className="text-[10px] uppercase tracking-widest font-bold text-primary animate-pulse">Extracting Metadata...</p>
              </div>
              <div className="absolute bottom-0 left-0 right-0 h-1 /shimmer" />
            </motion.div>
          ))}
          {items.map((item) => (
            <motion.div
              key={item.id}
              layoutId={`item-${item.id}`}
              className="group aspect-[3/4] rounded-3xl overflow-hidden glass border border-white/10 transition-smooth hover:border-primary/40 relative"
            >
              <img src={item.image} className="w-full h-full object-cover transition-smooth group-hover:scale-110" alt="Clothing Item" />
              <div className="absolute top-4 right-4 translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-smooth">
                <button className="p-2 rounded-lg glass bg-black/60 shadow-xl hover:text-primary"><Plus size={16} /></button>
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/90 via-black/40 to-transparent">
                <div className="flex flex-wrap gap-2">
                  {item.tags.map((tag, i) => (
                    <span key={i} className="px-3 py-1 rounded-full bg-primary/10 border border-primary/30 text-[10px] uppercase tracking-widest font-black text-primary">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default FitVault;
