import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.communication_scoring import score_text

samples = [
    "I have worked on several projects, like developing a web app. It was great.",
    "Um, I think I... actually, I built a system. It... you know, it was challenging.",
    "My experience includes leading a team of five engineers to deliver a cloud‑based solution on time and under budget."
]

for txt in samples:
    result = score_text(txt)
    print(f"Text: {txt}\nScore: {result['final_score']:.2f}\nBreakdown: {json.dumps(result['breakdown'], indent=2)}\n---\n")
