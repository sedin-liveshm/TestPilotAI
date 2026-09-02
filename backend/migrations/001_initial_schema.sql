-- TestPilot AI — Migration 001: Initial Schema & RLS Policies
-- Enables Supabase Auth integration, creates profiles, projects, tests tables,
-- foreign keys with cascading deletions, indexes, and strict Row Level Security (RLS).

-- ============================================================================
-- 1. PROFILES TABLE
-- Extends Supabase auth.users with application-level profile metadata.
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 2. PROJECTS TABLE
-- Represents a multi-tenant project owned by a specific profile.
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    base_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 3. TESTS TABLE
-- Stores automated test definitions with canonical Test IR (Intermediate Representation).
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    test_ir JSONB NOT NULL DEFAULT '{}'::jsonb,
    ir_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 4. INDEXES
-- Optimize performance for frequent foreign key and ownership filter queries.
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_projects_owner_id ON public.projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_tests_project_id ON public.tests(project_id);

-- ============================================================================
-- 5. ROW LEVEL SECURITY (RLS)
-- Enable RLS on all three base tables to enforce multi-tenant isolation.
-- ============================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tests ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 6. PROFILES POLICIES
-- Users can only read, update, or insert their own profile matching auth.uid().
-- ============================================================================
CREATE POLICY "Profiles select policy" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Profiles update policy" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Profiles insert policy" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- ============================================================================
-- 7. PROJECTS POLICIES
-- Users can only read, insert, update, or delete projects they own (owner_id = auth.uid()).
-- ============================================================================
CREATE POLICY "Projects select policy" ON public.projects
    FOR SELECT USING (auth.uid() = owner_id);

CREATE POLICY "Projects insert policy" ON public.projects
    FOR INSERT WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Projects update policy" ON public.projects
    FOR UPDATE USING (auth.uid() = owner_id);

CREATE POLICY "Projects delete policy" ON public.projects
    FOR DELETE USING (auth.uid() = owner_id);

-- ============================================================================
-- 8. TESTS POLICIES
-- Users can access tests only if they own the parent project (project_id -> projects.owner_id = auth.uid()).
-- ============================================================================
CREATE POLICY "Tests select policy" ON public.tests
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE public.projects.id = public.tests.project_id
              AND public.projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Tests insert policy" ON public.tests
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE public.projects.id = public.tests.project_id
              AND public.projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Tests update policy" ON public.tests
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE public.projects.id = public.tests.project_id
              AND public.projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Tests delete policy" ON public.tests
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE public.projects.id = public.tests.project_id
              AND public.projects.owner_id = auth.uid()
        )
    );

-- ============================================================================
-- 9. AUTOMATED PROFILE TRIGGER
-- Automatically creates a profile record when a new user signs up in Supabase Auth.
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        new.id,
        new.email,
        COALESCE(new.raw_user_meta_data->>'full_name', '')
    );
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
