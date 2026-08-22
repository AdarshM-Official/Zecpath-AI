# Signal-to-Score Mapping Model

## 1. Overview
Raw behavioral signals are normalized into three composite scores:
- **Focus Score (0–100)**
- **Confidence Score (0–100)**
- **Stress Indicator Score (0–100, where higher = more stress detected)**

These scores are additive context for the recruiter panel and are **not** combined into the Unified Hiring Fit percentage without explicit configuration.

---

## 2. Focus Score

**Formula:**
```
focus_score = (gaze_on_screen_pct * 0.50)
            + ((1 - distraction_event_ratio) * 0.30)
            + (sustained_attention_ratio * 0.20)
```

| Variable | Definition |
|---|---|
| `gaze_on_screen_pct` | % of total interview time gaze is on screen (0.0–1.0) |
| `distraction_event_ratio` | distraction events / max_expected_events (clamped 0–1) |
| `sustained_attention_ratio` | longest sustained attention window / total interview time |

**Interpretation:**
- 80–100: Highly focused, minimal distraction
- 60–79: Adequate focus, minor distraction
- 40–59: Moderate distraction — recruiter should review
- 0–39: High distraction — candidate may have environmental issues

---

## 3. Confidence Score

**Formula:**
```
confidence_score = (smile_freq_score * 0.30)
                 + (head_stability_score * 0.40)
                 + (facial_engagement_score * 0.30)
```

| Variable | Definition |
|---|---|
| `smile_freq_score` | Normalized count of genuine smile detections |
| `head_stability_score` | Inverse of head pose variance (high stability = high score) |
| `facial_engagement_score` | Ratio of frames with active facial muscle movement vs. static face |

---

## 4. Stress Indicator Score

**Formula:**
```
stress_score = (micro_expression_freq * 0.40)
             + (looking_away_event_count / 10 * 0.35)
             + (gaze_deviation_events / 10 * 0.25)
```
*(All values clamped to 0–1 before multiplication)*

**Interpretation:**
- This score is **not** presented negatively. A high stress score triggers a recruiter note: *"Candidate may have experienced interview anxiety. Consider follow-up conversation."*

---

## 5. Signal Processing Pipeline (Proposed)

```
[Webcam Frame]
      |
      v
[MediaPipe FaceMesh / dlib] ── Landmark Extraction
      |
      +─── Gaze Estimator ─────────► gaze_on_screen_pct, deviation_events
      |
      +─── Head Pose Estimator ────► yaw/pitch/roll variance, looking_away_events
      |
      +─── Expression Detector ────► smile_freq, micro_expression_freq
      |
      v
[BehavioralScoringEngine]
      |
      v
[Focus Score | Confidence Score | Stress Score]
      |
      v
[Recruiter Context Panel]
```
