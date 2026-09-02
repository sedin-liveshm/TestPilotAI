-- TestPilot AI — Development Seed Data & Instructions
-- Safe sample data for local testing of multi-tenant RLS isolation.
-- DO NOT RUN THIS IN PRODUCTION.

/*
===============================================================================
DEVELOPMENT SEED PROCEDURE
===============================================================================

Step 1: Register two test users in Supabase Auth (Dashboard or API/SDK):
  User A Email: user_a@example.com (Password: TestPassword123!)
  User B Email: user_b@example.com (Password: TestPassword123!)

Step 2: Obtain User A's ID and User B's ID from Supabase Auth (auth.users table).

Step 3: Execute the SQL statements below, replacing USER_A_UUID and USER_B_UUID
        with the actual UUIDs from Step 2.

===============================================================================
*/

-- Example SQL (Replace '00000000-0000-0000-0000-000000000001' with real User A UUID)
-- Example SQL (Replace '00000000-0000-0000-0000-000000000002' with real User B UUID)

-- Verify Profiles exist (Automatically populated by trigger or insert manually):
INSERT INTO public.profiles (id, email, full_name)
VALUES 
  ('00000000-0000-0000-0000-000000000001', 'user_a@example.com', 'User Alpha'),
  ('00000000-0000-0000-0000-000000000002', 'user_b@example.com', 'User Beta')
ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name;

-- Sample Projects:
INSERT INTO public.projects (id, owner_id, name, description, base_url)
VALUES
  (
    'a1111111-1111-1111-1111-111111111111',
    '00000000-0000-0000-0000-000000000001',
    'User A E-Commerce App',
    'Main web store frontend test suite',
    'https://store.example.com'
  ),
  (
    'b2222222-2222-2222-2222-222222222222',
    '00000000-0000-0000-0000-000000000002',
    'User B Portal Project',
    'Customer portal test suite',
    'https://portal.example.com'
  )
ON CONFLICT (id) DO NOTHING;

-- Sample Tests with Test IR:
INSERT INTO public.tests (id, project_id, name, description, test_ir, ir_version)
VALUES
  (
    'a9999999-9999-9999-9999-999999999999',
    'a1111111-1111-1111-1111-111111111111',
    'Login Smoke Test',
    'Validates customer login flow',
    '{
      "version": "1",
      "id": "login-smoke",
      "name": "Login smoke test",
      "actions": [
        { "type": "navigate", "url": "/login" },
        { "type": "fill", "target": { "strategy": "label", "value": "Email" }, "value": "user@example.com" },
        { "type": "click", "target": { "strategy": "role", "role": "button", "name": "Login" } },
        { "type": "assertVisible", "target": { "strategy": "role", "role": "heading", "name": "Dashboard" } }
      ]
    }'::jsonb,
    1
  ),
  (
    'b8888888-8888-8888-8888-888888888888',
    'b2222222-2222-2222-2222-222222222222',
    'Checkout Flow Test',
    'Validates customer checkout step',
    '{
      "version": "1",
      "id": "checkout-flow",
      "name": "Checkout Flow Test",
      "actions": [
        { "type": "navigate", "url": "/cart" },
        { "type": "click", "target": { "strategy": "role", "role": "button", "name": "Checkout" } },
        { "type": "assertUrl", "url": "/checkout" }
      ]
    }'::jsonb,
    1
  )
ON CONFLICT (id) DO NOTHING;
