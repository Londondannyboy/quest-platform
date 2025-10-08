-- Quest Platform v2.2 - Example Content Seed Data
-- Run this to populate a sandbox database with example articles
-- Usage: psql $DATABASE_URL -f backend/migrations/seed_example_data.sql

BEGIN;

-- Insert example articles for relocation.quest
INSERT INTO articles (
    id,
    slug,
    title,
    seo_title,
    seo_description,
    content,
    target_site,
    status,
    quality_score,
    word_count,
    reading_time_minutes,
    author,
    published_at,
    created_at,
    updated_at
) VALUES
(
    '550e8400-e29b-41d4-a716-446655440001',
    'portugal-digital-nomad-visa-complete-guide',
    'Portugal Digital Nomad Visa: Complete 2025 Guide',
    'Portugal Digital Nomad Visa: Complete 2025 Guide | Relocation Quest',
    'Everything you need to know about the Portugal Digital Nomad Visa in 2025. Requirements, application process, costs, and tax benefits explained.',
    '# Portugal Digital Nomad Visa: Complete 2025 Guide

Portugal has become one of the most popular destinations for digital nomads worldwide. The Portuguese government introduced a dedicated Digital Nomad Visa in 2022, making it easier than ever for remote workers to live and work legally in this beautiful European country.

## What is the Portugal Digital Nomad Visa?

The Portugal Digital Nomad Visa (officially called the "Temporary Stay Visa for the exercise of professional activity provided remotely") allows non-EU citizens to live in Portugal while working remotely for employers or clients based outside of Portugal.

### Key Benefits

- **Long-term stay**: Valid for up to 1 year, renewable
- **Schengen access**: Travel freely within the Schengen Area
- **Family inclusion**: Bring your spouse and dependents
- **Tax advantages**: Potential Non-Habitual Resident (NHR) tax regime benefits
- **Quality of life**: Affordable cost of living, excellent climate, vibrant expat community

## Eligibility Requirements

To qualify for the Portugal Digital Nomad Visa, you must meet these criteria:

### 1. Income Requirements

You must demonstrate a minimum monthly income of **€3,280** (approximately $3,500 USD) from remote work. This can be:

- Employment income from a foreign company
- Self-employment income from foreign clients
- Business income from a foreign-registered company

**Income Documentation:**
- Employment contract or letter from employer
- 3-6 months of bank statements
- Tax returns from previous year
- Proof of ongoing income stream

### 2. Remote Work Proof

You must provide evidence that:
- Your work is performed remotely via telecommunications
- Your employer/clients are based outside Portugal
- Your work does not compete with local Portuguese labor market

### 3. Health Insurance

Comprehensive health insurance covering:
- Medical expenses in Portugal
- Minimum coverage of €30,000
- Valid for the entire visa duration

### 4. Clean Criminal Record

- Police clearance certificate from home country
- Must be recent (within 3 months of application)

### 5. Accommodation Proof

Evidence of accommodation in Portugal:
- Rental agreement
- Property ownership documents
- Letter of invitation from a resident

## Application Process

### Step 1: Gather Documents (2-4 weeks)

Required documents:
- Valid passport (minimum 6 months validity)
- Visa application form (filled and signed)
- Two recent passport photos
- Proof of income and employment
- Health insurance certificate
- Criminal record certificate
- Proof of accommodation
- Portuguese tax number (NIF)

### Step 2: Submit Application (1-2 weeks)

- Apply at Portuguese consulate in your home country
- Schedule appointment online
- Submit all documents in person
- Pay visa fee: €90 (approximately $95 USD)

### Step 3: Wait for Decision (2-3 months)

- Processing time varies by consulate
- May be asked for additional documents
- Track status online

### Step 4: Collect Visa (1 week)

- Return to consulate to collect visa
- Visa valid for 120 days to enter Portugal

### Step 5: Register in Portugal (within 120 days)

- Enter Portugal within visa validity
- Apply for residence permit at SEF (Immigration Service)
- Provide biometric data
- Receive residence card (2-3 months)

## Costs Breakdown

| Item | Cost |
|------|------|
| Visa application fee | €90 |
| Residence permit | €170 |
| Health insurance (annual) | €500-€1,500 |
| Document translations | €200-€500 |
| Legal assistance (optional) | €500-€1,500 |
| **Total Estimated Cost** | **€1,460-€3,760** |

## Tax Implications

### Non-Habitual Resident (NHR) Regime

Digital nomads may qualify for Portugal''s NHR tax regime, offering:

- **0% tax** on most foreign-source income (if taxed in source country)
- **20% flat tax** on Portuguese-source income from certain activities
- Valid for **10 years**

**NHR Application:**
- Apply within first year of becoming Portuguese tax resident
- Requires proof of tax residency
- Free to apply (no application fee)

### When You Become a Tax Resident

You become a Portuguese tax resident if:
- You spend more than 183 days in Portugal in a calendar year
- You have a habitual residence in Portugal on December 31

## Best Cities for Digital Nomads

### Lisbon
- **Pros**: Vibrant startup scene, coworking spaces, international community
- **Cons**: Rising costs, tourist crowds
- **Average rent (1BR)**: €1,200-€1,800/month

### Porto
- **Pros**: Lower costs than Lisbon, beautiful architecture, growing tech scene
- **Cons**: Wetter climate, fewer international flights
- **Average rent (1BR)**: €800-€1,200/month

### Madeira (Funchal)
- **Pros**: Year-round sunshine, Digital Nomad Village program, stunning nature
- **Cons**: Island isolation, limited direct flights
- **Average rent (1BR)**: €600-€1,000/month

### The Algarve (Faro, Lagos)
- **Pros**: Beaches, golf courses, expat communities, lower costs
- **Cons**: Seasonal tourism, limited coworking spaces
- **Average rent (1BR)**: €700-€1,100/month

## Living Costs in Portugal

### Monthly Budget (Single Person)

| Category | Estimated Cost |
|----------|----------------|
| Rent (1BR apartment) | €800-€1,500 |
| Utilities (electricity, water, internet) | €80-€150 |
| Groceries | €200-€350 |
| Eating out | €150-€300 |
| Transport (monthly pass) | €40-€65 |
| Health insurance | €40-€120 |
| Coworking space | €100-€250 |
| Entertainment | €100-€200 |
| **Total** | **€1,510-€2,935** |

## Frequently Asked Questions

### Can I switch to a work visa later?

Yes, if you find a local job, you can apply to change your residence permit type.

### Can I bring my family?

Yes, your spouse and dependent children can apply for family reunification.

### Do I need to speak Portuguese?

No, it''s not required for the visa, but learning basic Portuguese is highly recommended.

### Can I work for Portuguese clients?

You can work for Portuguese clients as long as it''s not your primary income source and doesn''t compete with the local market.

### What if my application is rejected?

You can appeal the decision or reapply after addressing the rejection reasons.

## Conclusion

The Portugal Digital Nomad Visa offers an excellent pathway for remote workers to experience life in one of Europe''s most welcoming countries. With its combination of affordable living costs, excellent quality of life, and favorable tax regime, Portugal continues to attract digital nomads from around the world.

Start gathering your documents today, and you could be working from a Lisbon café or a Porto coworking space in just a few months!

---

**Last Updated**: October 2025

**Sources**: Portuguese Immigration and Borders Service (SEF), Portuguese Tax Authority, Expatica Portugal

**Disclaimer**: Visa requirements and processes may change. Always verify current requirements with official Portuguese government sources before applying.',
    'relocation',
    'published',
    92,
    2847,
    14,
    'Quest AI',
    NOW() - INTERVAL '7 days',
    NOW() - INTERVAL '7 days',
    NOW() - INTERVAL '7 days'
),
(
    '550e8400-e29b-41d4-a716-446655440002',
    'spain-vs-portugal-digital-nomad-comparison',
    'Spain vs Portugal for Digital Nomads: Complete Comparison 2025',
    'Spain vs Portugal for Digital Nomads: Which Country is Better in 2025?',
    'Comprehensive comparison of Spain and Portugal for digital nomads. Visa requirements, costs, lifestyle, taxes, and more.',
    '# Spain vs Portugal for Digital Nomads: Complete Comparison 2025

Choosing between Spain and Portugal as a digital nomad? Both Iberian neighbors offer excellent quality of life, but each has unique advantages. This comprehensive comparison will help you decide which country suits your remote work lifestyle better.

## Quick Comparison Table

| Factor | Portugal | Spain |
|--------|----------|-------|
| **Visa processing time** | 2-3 months | 3-4 months |
| **Minimum income requirement** | €3,280/month | €2,400/month |
| **Cost of living (capital)** | €1,800-€3,000/month | €2,200-€3,500/month |
| **Tax benefits** | NHR (10 years) | Beckham Law (6 years) |
| **English proficiency** | Moderate | Moderate-High |
| **Weather** | Atlantic (milder, wetter) | Mediterranean (hotter, drier) |
| **Digital nomad community** | Very strong | Very strong |

## Visa Requirements

### Portugal Digital Nomad Visa

**Pros:**
- Simpler application process
- Well-established program since 2022
- More consulate experience

**Cons:**
- Higher income requirement
- Longer initial processing time

**Income Requirement:** €3,280/month (~$3,500)

### Spain Digital Nomad Visa

**Pros:**
- Lower income requirement
- Longer initial validity (3 years)
- Larger country with more options

**Cons:**
- Newer program (launched 2023)
- Varying consulate efficiency
- More bureaucracy

**Income Requirement:** €2,400/month (~$2,600)

[... rest of the article continues with similar depth ...]',
    'relocation',
    'published',
    89,
    3124,
    15,
    'Quest AI',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days'
);

-- Insert example research cache entries
INSERT INTO article_research (
    id,
    query_text,
    embedding,
    research_results,
    sources,
    cache_hit_count,
    created_at
) VALUES
(
    '550e8400-e29b-41d4-a716-446655440101',
    'Portugal digital nomad visa requirements 2025',
    '[0.1, 0.2, 0.3, 0.4, 0.5]',  -- Placeholder embedding
    '{"key_facts": ["Minimum income €3,280/month", "Visa valid 1 year", "NHR tax benefits"], "summary": "Portugal offers attractive digital nomad visa with reasonable requirements"}',
    '["https://imigrante.sef.pt", "https://www.portugal.gov.pt", "https://www.portugalist.com"]',
    3,
    NOW() - INTERVAL '10 days'
);

-- Insert example article versions (for version history)
INSERT INTO article_versions (
    id,
    article_id,
    version_number,
    content,
    editor_notes,
    quality_score,
    created_by,
    created_at
) VALUES
(
    '550e8400-e29b-41d4-a716-446655440201',
    '550e8400-e29b-41d4-a716-446655440001',
    1,
    'Draft version before editing...',
    'Initial AI generation',
    78,
    'Quest AI',
    NOW() - INTERVAL '7 days'
),
(
    '550e8400-e29b-41d4-a716-446655440202',
    '550e8400-e29b-41d4-a716-446655440001',
    2,
    'Edited version with improved structure...',
    'Human editor improvements: Added FAQ section, improved readability',
    92,
    'Human Editor',
    NOW() - INTERVAL '7 days'
);

COMMIT;

-- Verify seed data
SELECT
    'Articles seeded: ' || COUNT(*)
FROM articles
WHERE id LIKE '550e8400-e29b-41d4-a716-44665544000%';

SELECT
    'Research cache entries: ' || COUNT(*)
FROM article_research
WHERE id LIKE '550e8400-e29b-41d4-a716-44665544010%';

SELECT
    'Article versions: ' || COUNT(*)
FROM article_versions
WHERE id LIKE '550e8400-e29b-41d4-a716-44665544020%';

-- Display seeded article titles
SELECT
    slug,
    title,
    status,
    quality_score,
    word_count
FROM articles
WHERE id LIKE '550e8400-e29b-41d4-a716-44665544000%'
ORDER BY created_at DESC;
