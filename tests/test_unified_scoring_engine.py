import pytest
from utils.unified_scoring_engine import UnifiedScoringEngine

def test_default_weights():
    engine = UnifiedScoringEngine(config_path="dummy_path.json")
    # By default weights are roughly equal (0.33, 0.33, 0.34)
    # ats: 1.0, screening: 1.0, hr: 1.0 -> 100%
    score = engine.compute_score(ats=1.0, screening=1.0, hr=1.0)
    assert score["hiring_fit_percent"] == 100.0

def test_role_adjustments():
    engine = UnifiedScoringEngine(config_path="config/unified_scoring_config.json")
    # Senior role weights: ats: 0.25, screening: 0.25, hr: 0.50
    score = engine.compute_score(ats=1.0, screening=1.0, hr=0.5, role="senior")
    # hiring_fit = (1.0 * 0.25) + (1.0 * 0.25) + (0.5 * 0.50) = 0.25 + 0.25 + 0.25 = 0.75 => 75.0%
    assert score["hiring_fit_percent"] == 75.0

def test_missing_role_fallback():
    engine = UnifiedScoringEngine(config_path="config/unified_scoring_config.json")
    # Using default weights (ats: 0.30, screening: 0.30, hr: 0.40) from our config file
    score = engine.compute_score(ats=1.0, screening=1.0, hr=0.5, role="unknown_role")
    # hiring_fit = (1.0 * 0.30) + (1.0 * 0.30) + (0.5 * 0.40) = 0.30 + 0.30 + 0.20 = 0.80 => 80.0%
    assert score["hiring_fit_percent"] == 80.0
