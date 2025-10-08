-- Quest Platform v2.2 - Database User Roles
-- Creates role-separated database users with least privilege
-- Run: psql $DATABASE_URL -f 002_create_users.sql

BEGIN;

-- ============================================================================
-- DATABASE USER ROLES (Least Privilege Principle)
-- ============================================================================

-- 1. fastapi_user (Application role for API + Workers)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'fastapi_user') THEN
        CREATE USER fastapi_user WITH PASSWORD '${FASTAPI_DB_PASSWORD}';
    END IF;
END
$$;

-- Grant DML permissions only (no DDL)
GRANT CONNECT ON DATABASE neondb TO fastapi_user;
GRANT USAGE ON SCHEMA public TO fastapi_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fastapi_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO fastapi_user;

-- Allow fastapi_user to use future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO fastapi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO fastapi_user;

-- 2. directus_user (CMS role - highly restricted)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'directus_user') THEN
        CREATE USER directus_user WITH PASSWORD '${DIRECTUS_DB_PASSWORD}';
    END IF;
END
$$;

-- Grant minimal permissions (only articles and users tables)
GRANT CONNECT ON DATABASE neondb TO directus_user;
GRANT USAGE ON SCHEMA public TO directus_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON articles, users TO directus_user;
GRANT USAGE, SELECT ON SEQUENCE articles_id_seq, users_id_seq TO directus_user;

-- CRITICAL: NO DDL permissions (prevents schema drift)
-- Directus will auto-discover schema but cannot modify it

-- 3. readonly_user (Analytics/Monitoring role)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'readonly_user') THEN
        CREATE USER readonly_user WITH PASSWORD '${READONLY_DB_PASSWORD}';
    END IF;
END
$$;

-- Read-only access to all tables
GRANT CONNECT ON DATABASE neondb TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Allow readonly_user to select from future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;

-- Grant access to monitoring views
GRANT SELECT ON daily_costs, cache_performance, quality_distribution TO readonly_user;

-- ============================================================================
-- VERIFY PERMISSIONS
-- ============================================================================

-- Check fastapi_user permissions
SELECT
    grantee,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'fastapi_user'
ORDER BY table_name, privilege_type;

-- Check directus_user permissions (should only have articles, users)
SELECT
    grantee,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'directus_user'
ORDER BY table_name, privilege_type;

-- Check readonly_user permissions (should have SELECT on all)
SELECT
    grantee,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'readonly_user'
ORDER BY table_name, privilege_type;

-- ============================================================================
-- CONNECTION STRINGS FOR REFERENCE
-- ============================================================================

-- fastapi_user connection string (for backend/.env):
-- DATABASE_URL=postgresql://fastapi_user:${FASTAPI_DB_PASSWORD}@ep-xxx.neon.tech/neondb?sslmode=require

-- directus_user connection string (for directus/.env):
-- DB_USER=directus_user
-- DB_PASSWORD=${DIRECTUS_DB_PASSWORD}

-- readonly_user connection string (for monitoring tools):
-- READONLY_DATABASE_URL=postgresql://readonly_user:${READONLY_DB_PASSWORD}@ep-xxx.neon.tech/neondb?sslmode=require

COMMIT;

-- ============================================================================
-- SECURITY NOTES
-- ============================================================================

/*
IMPORTANT SECURITY CONSIDERATIONS:

1. Password Management:
   - Replace ${FASTAPI_DB_PASSWORD}, ${DIRECTUS_DB_PASSWORD}, ${READONLY_DB_PASSWORD}
     with strong, unique passwords before running this script
   - Store passwords in environment variables, NOT in code
   - Rotate passwords quarterly

2. Schema Governance:
   - Only neondb_owner (DBA) can run DDL (CREATE, ALTER, DROP)
   - directus_user has NO DDL permissions → prevents UI-driven schema changes
   - All schema changes MUST go through migration files

3. Principle of Least Privilege:
   - fastapi_user: Full DML on all tables (application needs)
   - directus_user: DML only on articles, users (CMS needs)
   - readonly_user: SELECT only (monitoring/analytics)

4. Connection Security:
   - Always use SSL/TLS (sslmode=require)
   - Whitelist Railway IPs in Neon dashboard (optional but recommended)
   - Use connection pooling to limit concurrent connections

5. Audit Trail:
   - Enable pg_stat_statements for query monitoring
   - Log all DDL changes via migration files
   - Use created_at/updated_at for data audit

For more details, see: docs/schema-governance.md
*/
