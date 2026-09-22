-- =====================================================================
-- CUSTOMER MARKETING & RETENTION ANALYTICS - DATABASE SCHEMA
-- =====================================================================
-- Run this once against a fresh Postgres/Supabase database before
-- pointing marketing_ingestion.py at it with real credentials. The table
-- below matches exactly what marketing_ingestion.py writes to.

CREATE TABLE IF NOT EXISTS public.marketing_churn_raw (
    "CustomerID" TEXT PRIMARY KEY,
    "CustomerSegment" TEXT NOT NULL,
    "AcquisitionChannel" TEXT,
    "TenureMonths" INTEGER NOT NULL CHECK ("TenureMonths" >= 0),
    "SupportCalls" REAL CHECK ("SupportCalls" >= 0 OR "SupportCalls" IS NULL),
    "TotalSpend_USD" REAL CHECK ("TotalSpend_USD" >= 0 OR "TotalSpend_USD" IS NULL),
    "ChurnStatus" INTEGER NOT NULL CHECK ("ChurnStatus" IN (0, 1)),
    "data_quality_status" TEXT NOT NULL DEFAULT 'CLEAN'
);

CREATE INDEX IF NOT EXISTS idx_marketing_segment ON public.marketing_churn_raw ("CustomerSegment");
CREATE INDEX IF NOT EXISTS idx_marketing_churn ON public.marketing_churn_raw ("ChurnStatus");

-- =====================================================================
-- ROW-LEVEL SECURITY
-- =====================================================================
ALTER TABLE public.marketing_churn_raw ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Authenticated read access" ON public.marketing_churn_raw;
CREATE POLICY "Authenticated read access" ON public.marketing_churn_raw
    FOR SELECT TO authenticated USING (true);
