# Zecpath-AI Live Demo Script

**Target Audience:** C-Suite, VP of Engineering, HR Leadership
**Estimated Time:** 8 Minutes
**Prerequisites:** 
- Zecpath-AI repository cloned and dependencies installed.
- Ensure terminal output is visible on the projector/screen.

---

## Part 1: Introduction (1 min)

**Speaker:** 
> "Welcome everyone. Today, I'm going to demonstrate Zecpath-AI, our fully autonomous technical interviewing system. 
> 
> Rather than showing you a mock UI, we are going to look under the hood. I'm going to run a live simulation that passes three distinct candidate personas through our actual production AI pipeline. We'll see how the system evaluates a Strong Senior, a Weak Junior, and crucially, a candidate attempting to cheat the system."

---

## Part 2: Running the Pipeline (2 mins)

**Action:** Open terminal and run:
```bash
python demo/simulate_full_pipeline.py
```

**Speaker:** 
> *(While the script initializes)*
> "The system is now booting our `InterviewConversationFlow`. It is ingesting the candidates' mock ATS scores and beginning the conversational HR and Technical rounds.
>
> **Look at Candidate 1: Alex Mercer.** Alex is giving detailed, structured answers about microservices and Kafka. You can see the NLP engine assigning high confidence and communication scores in real-time.
>
> **Now look at Candidate 2: Jordan Lee.** Jordan is using filler words and giving very shallow answers. Notice how the HR Scoring Engine instantly drops their score due to poor consistency and low relevance."

---

## Part 3: The Integrity Override (2 mins)

**Action:** Highlight the terminal output where "Casey Smith" is processed.

**Speaker:**
> "Here is where Zecpath-AI shines. Candidate 3, Casey Smith, gives absolutely perfect, textbook answers for time complexity and system design. A standard automated system would hire them immediately. 
>
> However, our background `MalpracticeDetector` is analyzing the candidate's browser and behavioral context. Notice these red alerts populating in the terminal:
> `[ALERT][CRITICAL] Tab switch count reached 12. Possible lookup behavior.`
> `[ALERT][WARNING] Repeated off-screen gaze detected.`
>
> The system has recognized that Casey is repeatedly switching tabs and looking off-screen to read answers. The Final Recommendation Engine intercepts the perfect test score, flags the integrity risk, and outputs an automatic **REJECTED**."

---

## Part 4: Reviewing the Outputs (2 mins)

**Action:** Open the `reports/c_alex_senior_01_report.md` and `reports/c_casey_suspicious_03_report.md` files side-by-side in a Markdown viewer.

**Speaker:**
> "Finally, let's look at what the recruiter actually sees. Zecpath-AI compiles millions of data points from the interview into these highly readable, single-page Markdown reports.
>
> On the left, Alex is clearly marked as **🟢 SELECTED**, with a complete stage-by-stage breakdown and AI explanation. 
>
> On the right, Casey is marked as **🔴 REJECTED**. The recruiter doesn't have to guess why; the report clearly highlights the critical Integrity Alerts, noting the severe tab switching and gaze deviations.
>
> This is how Zecpath-AI guarantees that you only spend human time interviewing the absolute best—and most honest—candidates."

---
*End of Demo*
