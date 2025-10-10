# Generate Article Command

Generate a new article using the Quest Platform article generation pipeline.

## Instructions

When the user runs `/generate`, you should:

1. **Ask for the topic** (if not provided)
2. **Confirm the target site** (default: relocation)
3. **Run the generation script:**
   ```bash
   cd /Users/dankeegan/quest-platform/backend
   python3 generate_article.py --topic "TOPIC_HERE" --site relocation
   ```

4. **Report the results:**
   - Quality score
   - Cost
   - URL where article will be live
   - Any errors or warnings

## Options

- `--site` - Target site: `relocation`, `placement`, or `rainmaker` (default: relocation)
- `--batch FILE` - Generate multiple articles from a file
- `--count N` - Generate N articles
- `--concurrent N` - Run N generations in parallel

## Examples

**Single article:**
```
/generate "Best digital nomad cities in Asia 2025"
```

**Batch generation:**
```
/generate --batch topics.txt --count 5
```

## Notes

- The script uses the full 7-agent pipeline
- Images are generated automatically
- Articles auto-publish if quality score ≥ 75
- Cost is typically $0.20-$0.40 per article
