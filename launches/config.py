"""Configuration constants for the orchestrator."""

# Model settings
MODEL = "claude-sonnet-4-20250514"
MANAGER_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
MANAGER_MAX_TOKENS = 2048

# Concurrency
MAX_CONCURRENT_AGENTS = 20

# Quality gates
REQUIRED_SCORE = 10
MAX_MANAGER_ITERATIONS = 5

# Hook settings
HOOK_STYLES = ["contrarian", "story", "statistic", "question"]
NUM_HOOKS = 4

# CTA settings
CTA_STYLES = ["direct", "soft"]
NUM_CTAS = 2

# Weapons check
WEAPONS_BATCH_SIZE = 5
FILLER_THRESHOLD = 5  # Lines with both scores <= this get cut

# Character budgets
DEFAULT_CHAR_BUDGET = 3000

# Research settings
YOUTUBE_KEYWORDS_COUNT = 15
YOUTUBE_TIME_FILTERS = ["all_time", "last_12_months", "last_30_days"]

# Hook manager scoring dimensions
HOOK_DIMENSIONS = [
    "scroll_stop_power",
    "specificity",
    "emotional_voltage",
    "curiosity_gap",
    "brand_voice_match",
]

# Body manager scoring dimensions
BODY_DIMENSIONS = [
    "narrative_flow",
    "specificity",
    "emotional_resonance",
    "product_clarity",
    "pacing",
]

# CTA manager scoring dimensions
CTA_DIMENSIONS = [
    "urgency",
    "clarity",
    "emotional_pull",
    "specificity",
    "action_friction",
]
