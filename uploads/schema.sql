-- ClosetMind AlloyDB Schema for Profile and Wardrobe
-- Enable pgvector for style-based searching
CREATE EXTENSION IF NOT EXISTS vector;

-- Table for User Profiles
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    gender TEXT,
    location TEXT,
    selfie_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for Wardrobe Items (Used by parallel vision agents)
CREATE TABLE IF NOT EXISTS wardrobe (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    image_url TEXT NOT NULL,
    category TEXT,
    color TEXT,
    tags TEXT[],
    embedding vector(768), -- For RAG-based styling (Gemini Embeddings)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for vector search (Cosine Similarity)
CREATE INDEX IF NOT EXISTS wardrobe_embedding_idx ON wardrobe USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
