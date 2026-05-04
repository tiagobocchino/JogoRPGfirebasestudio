-- 1. Atualizar Tabela de Personagens (Adicionar colunas se não existirem)
ALTER TABLE characters ADD COLUMN IF NOT EXISTS race TEXT DEFAULT 'Humano';
ALTER TABLE characters ADD COLUMN IF NOT EXISTS age INTEGER DEFAULT 20;
ALTER TABLE characters ADD COLUMN IF NOT EXISTS backstory TEXT;
ALTER TABLE characters ADD COLUMN IF NOT EXISTS skills_points INTEGER DEFAULT 0;
ALTER TABLE characters ADD COLUMN IF NOT EXISTS spell_points INTEGER DEFAULT 0;

-- 2. Tabela de Configuração de Servidores
CREATE TABLE IF NOT EXISTS guild_configs (
    guild_id TEXT PRIMARY KEY,
    lobby_channel_id TEXT,
    music_channel_id TEXT,
    admin_channel_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Limpar e recriar Políticas para evitar erros
DROP POLICY IF EXISTS "SelectOwnCharacters" ON characters;
DROP POLICY IF EXISTS "PublicAccess" ON characters;
DROP POLICY IF EXISTS "PublicSessions" ON game_sessions;
DROP POLICY IF EXISTS "PublicConfigs" ON guild_configs;

-- 4. Novas Políticas
CREATE POLICY "PublicAccess" ON characters FOR ALL USING (true);
CREATE POLICY "PublicSessions" ON game_sessions FOR ALL USING (true);
CREATE POLICY "PublicConfigs" ON guild_configs FOR ALL USING (true);

-- Habilitar RLS (caso não esteja)
ALTER TABLE characters ENABLE ROW LEVEL SECURITY;
ALTER TABLE game_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE guild_configs ENABLE ROW LEVEL SECURITY;
