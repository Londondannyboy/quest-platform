#!/usr/bin/env python3
"""Quick script to check article references"""

import psycopg2
import os

# Database connection
conn = psycopg2.connect(
    host="ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_Q9VMTIX2eHws"
)

cursor = conn.cursor()
cursor.execute("""
    SELECT content
    FROM articles
    WHERE title = 'Malta Gaming License 2025: Complete Cost Breakdown and Application Guide'
    ORDER BY created_at DESC
    LIMIT 1
""")

article = cursor.fetchone()
if article:
    content = article[0]

    # Check for References section
    has_references = "## References" in content or "## Sources" in content

    # Count citations
    citation_count = content.count("[")

    # Get last 2000 chars to see end of article
    tail = content[-2000:]

    print(f"Has References section: {has_references}")
    print(f"Total '[' brackets (approx citations): {citation_count}")
    print(f"\n=== LAST 2000 CHARACTERS ===\n")
    print(tail)

    # Check for hyperlinks
    hyperlink_count = content.count("](http")
    print(f"\n\nHyperlink count: {hyperlink_count}")
else:
    print("Article not found")

cursor.close()
conn.close()
