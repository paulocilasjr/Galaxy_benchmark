# Scoring Specification

## 1. Run-level performance

Define run performance:

Perf(t,p,e) = w_c*C + w_x*X + w_s*S + w_r*R + w_i*I

Where:
- C = correctness
- X = execution success
- S = scientific validity
- R = reproducibility / provenance
- I = interpretation or iteration quality

All component scores should be normalized to [0,1].

Recommended default weights:
- w_c = 0.35
- w_x = 0.20
- w_s = 0.20
- w_r = 0.15
- w_i = 0.10

Weights should be configurable per task family.

## 2. Task-level performance by environment

Perf(t,e) = Σ_p w_p * Perf(t,p,e)

Default prompt weights:
- vague = 0.33
- specific = 0.33
- very_specific = 0.34

Alternative practical-support weighting:
- vague = 0.40
- specific = 0.35
- very_specific = 0.25

## 3. Robustness

Robust(t,e) = α * mean_p(Perf(t,p,e)) - β * var_p(Perf(t,p,e))

Recommended defaults:
- α = 1.0
- β = 0.5

Interpretation:
- high mean across prompts is good
- high variance across prompts is bad

## 4. Adaptability

Galaxy adaptation:
Adapt_G(t,p) = Perf(t,p,galaxy) - Perf(t,p,open)

Skills adaptation:
Adapt_S(t,p) = Perf(t,p,galaxy_skills) - Perf(t,p,galaxy)

Prompt-aggregated:
Adapt_G(t) = Σ_p w_p * Adapt_G(t,p)
Adapt_S(t) = Σ_p w_p * Adapt_S(t,p)

## 5. Benchmark-level aggregation

Overall performance in environment e:
Perf(e) = Σ_t w_t * Perf(t,e)

Overall robustness in environment e:
Robust(e) = Σ_t w_t * Robust(t,e)

Overall adaptability:
Adapt_G = Σ_t w_t * Adapt_G(t)
Adapt_S = Σ_t w_t * Adapt_S(t)

Suggested task weighting:
- equal per complexity tier, then equal within tier

## 6. User-level confidence

Map prompts to user levels:
- vague -> novice
- specific -> intermediate
- very_specific -> expert

For prompt p and environment e:
ULC(p,e) = count_t[ Perf(t,p,e) >= tau ] / |T|

Suggested thresholds:
- usable: tau = 0.70
- reliable: tau = 0.85
- expert-grade: tau = 0.93

## 7. Pseudocode

```python
def run_performance(component_scores, weights):
    return sum(component_scores[k] * weights[k] for k in weights)

def task_performance(prompt_scores, prompt_weights):
    return sum(prompt_scores[p] * prompt_weights[p] for p in prompt_weights)

def robustness(prompt_scores, alpha=1.0, beta=0.5):
    vals = list(prompt_scores.values())
    mean = sum(vals) / len(vals)
    var = sum((x - mean) ** 2 for x in vals) / len(vals)
    return alpha * mean - beta * var

def adaptability(scores_a, scores_b, prompt_weights):
    return sum(prompt_weights[p] * (scores_b[p] - scores_a[p]) for p in prompt_weights)

def user_level_confidence(task_prompt_scores, threshold):
    passed = sum(1 for score in task_prompt_scores if score >= threshold)
    return passed / len(task_prompt_scores)
```
