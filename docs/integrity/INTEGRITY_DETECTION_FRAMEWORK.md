# Integrity Detection Framework

## 1. Objective
Detect and flag potential malpractice or academic dishonesty during AI-conducted interviews **in a fair, non-accusatory manner**. The system is advisory — all flags are surfaced to a human reviewer, never used for automatic disqualification.

> [!IMPORTANT]
> Integrity detection must balance security with candidate fairness. Every flag must carry an evidence summary and confidence level so human reviewers can dismiss false positives.

---

## 2. Malpractice Signal Taxonomy

### Category A — Browser / Application Signals (Detectable via Frontend)
| Signal | Description | Capture Method |
|---|---|---|
| **Tab switching** | Candidate switches away from the interview tab | `document.visibilitychange` event |
| **Screen focus loss** | Browser window loses focus (alt-tab to another app) | `window.blur` / `window.focus` events |
| **Copy-paste activity** | Candidate pastes text into a text-input field | `paste` event listener |
| **DevTools open** | Browser DevTools detected (e.g., window resize heuristic) | Window dimension delta check |

### Category B — Audio Signals (Detectable via Microphone)
| Signal | Description |
|---|---|
| **Multiple voices** | A second distinct voice is detected during the candidate's speaking turn |
| **Coaching whispers** | Low-volume background voice overlapping with candidate speech |
| **Suspicious silence breaks** | Long pauses followed by near-perfect answers (suggests looking up answers) |

### Category C — Behavioral / Visual Signals (Integrated from Day 48 Behavioral AI)
| Signal | Description |
|---|---|
| **Repeated looking away** | Frequent large gaze/head deviations (>30° yaw) more than 5 times per question |
| **Reading pattern** | Consistent horizontal eye movement suggesting reading from another source |
| **Sudden performance spike** | Dramatic jump in answer quality after a long pause |

---

## 3. Integration with Behavioral Signals
The Integrity Detection module subscribes to the same signal stream as the Day 48 Behavioral Analyzer:

```
[Webcam / Mic / Browser Events]
          |
          +──► BehavioralAnalyzer (Focus, Confidence, Stress)
          |
          +──► IntegrityDetector (Flags, Risk Tags, Alerts)
                    |
                    v
          [IntegrityReport + RiskTag appended to CandidateReport]
```

Thresholds defined for integrity are deliberately **stricter** than behavioral ones. A candidate may look away once due to nerves; looking away repeatedly at the same angle on every answer is a different signal pattern.
