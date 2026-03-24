"""Configuration constants for the content generator."""

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

# Platform settings
PLATFORMS = ["linkedin", "twitter", "email"]

# Voice check
VOICE_CHECK_BATCH_SIZE = 5
FILLER_THRESHOLD = 5  # Lines with both scores <= this get cut

# LinkedIn manager scoring dimensions
LINKEDIN_DIMENSIONS = [
    "voice_match",
    "hook_power",
    "value_density",
    "engagement_potential",
    "professional_tone",
]

# Twitter manager scoring dimensions
TWITTER_DIMENSIONS = [
    "voice_match",
    "scroll_stop_power",
    "conciseness",
    "shareability",
    "conversation_starter",
]

# Email manager scoring dimensions
EMAIL_DIMENSIONS = [
    "voice_match",
    "subject_line_power",
    "opening_hook",
    "value_delivery",
    "cta_clarity",
]
