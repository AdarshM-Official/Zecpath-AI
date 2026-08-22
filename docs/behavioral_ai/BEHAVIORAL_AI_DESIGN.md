# Behavioral AI Design Document

## 1. Objective
Supplement the HR and Technical interview scoring with non-invasive behavioral signals captured via webcam during a video interview. The goal is to surface attention, engagement, and stress indicators that may not be visible in the transcript alone.

> **Ethical Note:** All behavioral analysis must be disclosed to the candidate in the consent form. No signal is used as a sole disqualification criterion. Signals are advisory — they feed into the recruiter's context panel, not the automated score.

---

## 2. Observable Signal Categories

### 2.1 Eye Movement & Gaze Stability
Tracked using a webcam + a lightweight gaze estimation library (e.g., OpenCV + dlib, or MediaPipe FaceMesh).

| Signal | Description | Threshold |
|---|---|---|
| **Gaze-on-screen %** | % of time the candidate is looking at the camera/screen zone | <60% indicates distraction |
| **Gaze deviation events** | Count of times gaze moves off-screen for >2 seconds | >5 events = high distraction |
| **Reading pattern** | Horizontal left-right eye movement suggests reading from notes | Flagged if >3 clusters detected |

### 2.2 Head Movement
| Signal | Description | Threshold |
|---|---|---|
| **Head pose stability** | Variance of yaw/pitch/roll angles over time | High variance = restlessness |
| **Nodding frequency** | Vertical head movement correlated with speech | Natural nodding is positive; excessive may indicate anxiety |
| **Looking away events** | Sudden large yaw rotation (>30°) | >4 events per question = flag |

### 2.3 Facial Engagement
| Signal | Description |
|---|---|
| **Expression presence** | Are facial muscles active (engaged) or static (disengaged)? |
| **Smile frequency** | Positive signal for confidence and rapport |
| **Micro-expression frequency** | Rapid facial changes may signal stress or cognitive load |

### 2.4 Attention Patterns
| Signal | Description |
|---|---|
| **Sustained attention windows** | Longest unbroken period of on-screen gaze |
| **Recovery time** | How quickly candidate returns focus after a distraction |
| **Peak distraction timestamps** | Times of greatest off-screen behavior (useful context for recruiters) |

---

## 3. Non-Invasive Principles
- **No emotion classification:** The system does not classify emotions as "happy", "sad", or "angry". It measures *engagement signals* (attention, focus) only.
- **No biometric storage:** Raw video frames are processed in real-time and immediately discarded. Only derived signal scores are stored.
- **Opt-in only:** If the candidate's device does not have a camera or they opt out, behavioral scoring is simply omitted from the report.
