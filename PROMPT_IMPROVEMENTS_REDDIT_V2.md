# Content Prompt Improvements - Reddit Research V2

**Source:** r/ChatGPTPromptGenius - "I finally found a prompt that makes ChatGPT write naturally"
**Date:** October 10, 2025
**Status:** To be implemented after initial testing

---

## 🎯 Summary

This document captures additional natural language improvements from Reddit that should be added to our ContentAgent prompts AFTER we validate the current version (commit `7836920`) with test articles.

---

## 🚫 Forbidden Words (AI Giveaways)

### Words to Ban:
```
dive, unlock, unleash, intricate, utilization, transformative, alignment,
proactive, scalable, benchmark, delve, opt, realm, bustling, vibrant,
crucial, essential, vital, keen, fancy, labyrinth, gossamer, enigma,
indelible, meticulous, complexities, everchanging, ever-evolving, daunting,
cutting-edge, robust, tapestry, metropolis, reverberate, promptly
```

### Phrases to Ban:
```
"in today's world"
"in today's world"
"at the end of the day"
"on the same page"
"end-to-end"
"in order to"
"best practices"
"dive into"
"it's not just a..., it's a..."
"Let me explain"
"You know what?"
"Here's the thing"
"I hope this email finds you well"
"it's important to note"
"it's critical to"
"in summary"
"remember that"
"furthermore"
"additionally"
"consequently"
"importantly"
"indeed"
"notably"
"arguably"
"you may want to"
"on the other hand"
"as previously mentioned"
"it's worth noting that"
"to summarize"
"ultimately"
"to put it simply"
```

### Action Words to Avoid:
```
navigating, embark, mastering, excels, imagine, enhance,
emphasise/emphasize, revolutionize, foster, subsequently,
whispering
```

---

## ✅ Writing Style Enhancements

### Sentence & Paragraph Structure:
- **Mix sentence lengths:** Short (5-10 words) + Medium (15-20) + Long (25-30)
- **Paragraph lengths:** 1 to 7 sentences (vary dynamically)
- **Flesch Reading Ease:** Target score of 80
- **25% of sentences:** Keep under 20 words
- **Active voice:** >90% of content (passive voice <10%)

### Punctuation Variety:
- Use dashes naturally — like this
- Use semicolons for related ideas; they connect well
- Use parentheses (sparingly) for asides
- It's okay to break grammar rules slightly if it sounds real

### Natural Language Elements:
```
✅ Start sentences with "and" or "but"
✅ Use contractions (it's, don't, you're)
✅ Use idioms and colloquialisms
✅ Casual phrases (sparingly): "Honestly", "You know", "Just"
✅ Mild repetition for emphasis (humans do this naturally)
✅ Small tangents that connect back to main point
✅ Sensory details when they enhance clarity
```

---

## 📊 Specific Prompt Additions

### Add to System Prompt:
```
Your writing must pass AI detection as human-written. Key requirements:
- Flesch Reading Ease score around 80
- Mix sentence lengths (5-30 words)
- Vary paragraph lengths (1-7 sentences)
- Use contractions naturally (it's, don't, you're)
- Start sentences with "and" or "but" when natural
- Use dashes, semicolons, parentheses for variety
- Include mild repetition for emphasis (like humans do)
- Allow small tangents that connect back to the point
```

### Add to Content Prompt (Forbidden Words Section):
```
**CRITICAL - NEVER USE THESE AI-GIVEAWAY WORDS:**
- dive, unlock, unleash, delve, opt, transformative, robust, crucial, vital
- realm, bustling, vibrant, meticulous, complexities, tapestry, cutting-edge

**CRITICAL - NEVER USE THESE AI-GIVEAWAY PHRASES:**
- "in today's world" / "at the end of the day" / "best practices"
- "dive into" / "it's not just a..., it's a..." / "on the other hand"
- "it's worth noting" / "to summarize" / "furthermore" / "additionally"

**CRITICAL - WRITE NATURALLY:**
- It's okay to start sentences with "and" or "but"
- Use contractions (it's, don't, you're, we're)
- Mix short punchy sentences with longer flowing ones
- Vary paragraph lengths (1-7 sentences)
- Include mild repetition for emphasis (humans do this)
- Use dashes — like this — for natural pauses
```

---

## 🎓 User Feedback from Reddit

### What Works:
1. **"Flesch Reading Ease score around 80"** - Consistently followed by AI
2. **Forbidden word lists** - Dramatically improves natural tone
3. **"Write as you normally speak"** - Simple but effective
4. **"Avoid marketing language"** - Removes hype
5. **"Don't stress perfect grammar"** - Allows natural flow

### What Doesn't Work:
1. **Word count requirements** - AI unreliable at counting (use Sonnet to compensate)
2. **Too many instructions** - After ~20 rules, AI ignores some
3. **Over-prescription** - Too rigid = heuristic bias

### Pro Tips from Power Users:
1. **Break into chunks** - Multiple prompts instead of one mega-prompt
2. **Iterative refinement** - First draft, then "make it more human"
3. **Feed samples** - Give AI examples of your actual writing style
4. **Simple override** - "No BS, be honest, use familiar tone"
5. **Dialect touch** - "Write at 6th grade level" for social media

---

## 📝 Implementation Priority

### Phase 1: Already Implemented (Commit `7836920`)
- ✅ Elite-level SEO expert framing
- ✅ Competitive positioning ("OUTRANK competitors")
- ✅ Natural language emphasis ("never robotic")
- ✅ Strict word count (3000+ required)

### Phase 2: Test Current Changes
- ⏳ Generate 3 test articles (Malta, Portugal, Cyprus)
- ⏳ Verify Sonnet generates 3000+ words
- ⏳ Check for "robotic" language
- ⏳ Validate refinement system works

### Phase 3: Add Forbidden Words (After Testing)
- 📋 Add forbidden words list to content.py
- 📋 Add forbidden phrases list to content.py
- 📋 Add sentence/paragraph variety instructions
- 📋 Add Flesch Reading Ease target
- 📋 Test again with Malta article

### Phase 4: Fine-Tuning (Week 2)
- 📋 Add punctuation variety instructions
- 📋 Add natural language elements (contractions, "and"/"but" starts)
- 📋 Reduce instruction count (keep under 20 rules)
- 📋 A/B test with/without changes

---

## 🔬 Testing Methodology

### AI Detection Tools (Per Reddit):
1. **Quillbot** - Most lenient
2. **Originality.ai** - Hardest to pass
3. **ZeroGPT** - Mid-range

### Success Metrics:
- **Flesch Reading Ease:** 75-85 range
- **AI Detection:** <40% flagged as AI
- **Word Count:** 3000-4000 words consistently
- **Natural Tone:** No "robotic" phrases in manual review

### Test Process:
1. Generate article with current prompts
2. Run through Quillbot/Originality.ai
3. Manual review for forbidden words
4. Calculate Flesch score
5. User feedback on naturalness

---

## 💡 Key Insights

### From TooBusyforReddit (841 upvotes):
> "I fine-tuned this prompt over several weeks. ChatGPT still doesn't follow 100%, but I get 60-70% human detection on Quillbot."

**Lesson:** Perfect detection is impossible; 60-70% human is excellent.

### From BenAttanasio (OP):
> "I've noticed any more than around 20 distinct instructions, the AI doesn't account for them all."

**Lesson:** Keep total instructions under 20 rules.

### From hawkweasel:
> "AI is extremely unreliable at word counts. It seems to do better at sentence count or paragraph count."

**Lesson:** Use Sonnet (not Haiku) for word count reliability + strong emphasis.

### From paradite:
> "Break it up to multiple steps. First step focus on replacing words, second step sentence structure, etc."

**Lesson:** This is EXACTLY what our refinement system does!

---

## 🚀 Next Steps

**Immediate (Tonight):**
1. Test current prompts (commit `7836920`)
2. Validate Sonnet + refinement system
3. Review Malta article for natural language

**Week 1 (After Validation):**
4. Add forbidden words/phrases list
5. Add Flesch Reading Ease target
6. Add sentence/paragraph variety instructions
7. Test again

**Week 2 (Fine-Tuning):**
8. Reduce instruction count to <20 rules
9. A/B test prompt variations
10. Measure AI detection scores

---

## 📊 Expected Impact

**Before (Current - Commit 7836920):**
- Competitive framing ✅
- Natural language emphasis ✅
- 3000+ word requirement ✅
- Expected AI detection: 50-60% flagged

**After (With Forbidden Words):**
- All above +
- Forbidden words banned ✅
- Forbidden phrases banned ✅
- Sentence/paragraph variety ✅
- Expected AI detection: 30-40% flagged (GOAL!)

---

**Status:** Ready to implement after Phase 2 testing complete
**Estimated Implementation Time:** 1-2 hours
**Expected Quality Improvement:** 15-20% better AI detection pass rate
