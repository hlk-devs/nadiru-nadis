# nadi-deepreview

**Three-stage code review pipeline. Two AI reviewers from different providers analyze your code independently, then a third AI integrates both reviews and produces corrected code.**

This is the most ambitious Nadi in the collection and the best demonstration of what becomes possible when an orchestration layer can route tasks across providers. Single-provider code review is just one model's opinion. Multi-provider independent review surfaces issues that any single model would miss, then has a third model arbitrate. The result is genuinely better than what any one provider could produce alone.

## How it works

1. **Reviewer A** (Provider 1): Reviews your code as a senior dev. Documents every issue with severity, category, and recommendations. Makes no changes.
2. **Reviewer B** (Provider 2): Reviews the same code independently. Different provider, different training data, different blind spots. Makes no changes.
3. **Integration Architect** (Provider 3): Reads both reviews, identifies agreements and disagreements, decides which recommendations to implement, and produces the final corrected code with full documentation of every decision.

All three stages use different AI providers for genuinely independent perspectives. The Integration Architect can also choose to reject recommendations from either reviewer if it disagrees, which is a useful check against false positives.

## Usage
