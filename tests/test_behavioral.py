import json
from interview_ai.behavioral_report import BehavioralReporter

def main():
    reporter = BehavioralReporter()
    
    sample_text = "Um, I think I am a great fit for this role. I mean, I have excellent skills but... I am not sure if I can start immediately. However, I am confident I will succeed."
    duration = 15.0 # seconds
    
    report = reporter.generate_report(sample_text, duration)
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    main()
