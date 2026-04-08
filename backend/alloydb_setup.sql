-- ClosetMind AlloyDB Schema (PostgreSQL)
-- Execute this in your AlloyDB console or via psql

-- 1. Create Users table for profile persistence
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT,
    location TEXT,
    selfie_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Wardrobe table for AI ingestion (pgvector required)
CREATE TABLE IF NOT EXISTS wardrobe (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    category TEXT,
    color TEXT,
    material TEXT,
    tags TEXT[],
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
