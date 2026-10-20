---
name: model-fitting-setup-validation
description: Use before fitting or accepting regression, curve-fitting, model-comparison, prediction, or optimization results when row scope, response/predictor semantics, controls or endpoints, replicates, transformations, model metrics, or the evaluation domain can change the answer. Skip direct summaries and correlations without model fitting.
---

# Model Fitting Setup Validation

Make the estimand and fitted data explicit before comparing or accepting
models.

## Setup

Resolve the applicable choices:

- requested output: prediction, optimum location, response at the optimum,
  model metric, coefficient, p-value, class, or another quantity;
- response and predictor definitions, units, transformations, and category or
  event orientation;
- included row scope, controls, baselines, endpoints, missing values, and
  replicate handling;
- candidate models, formulas, fixed parameters, and fitting implementation;
- comparison metric and convention; and
- evaluation or optimization domain and final extraction rule.

These choices must follow the task and data semantics rather than tool defaults
or whichever rows are easiest to fit.

## Row And Predictor Scope

- Fit compared candidates on the same effective observations unless the task
  explicitly defines different subsets. Verify row counts after filtering,
  formula evaluation, and missing-value handling.
- Include a control or boundary row only when it belongs to the modeled
  response curve or estimand. Exclude unrelated controls, backgrounds, or
  component systems.
- Preserve raw replicates, paired observations, or aggregated entities according
  to the experimental unit. Do not silently average repeated labels.
- For ratios, mixtures, doses, frequencies, or proportions, identify the focal
  component and token order from component labels or documented metadata before
  converting text to a numeric predictor. Equal ratio strings do not imply the
  same predictor when their component systems differ.
- For a two-component proportion axis, pure rows measured under the same assay,
  response definition, background, and component system are candidate observed
  boundaries: the pure focal component is `p=1` and the pure counterpart is
  `p=0`. Treat the endpoints symmetrically. Include both when the estimand is the
  full response curve; exclude both when the task explicitly restricts the fit
  to interior mixtures. Do not include only the endpoint that produces a
  preferred fit.
- If endpoint membership is genuinely ambiguous and materially affects the
  requested result, compare the interior-only scope with the complete set of
  same-system observed boundaries while holding every other modeling choice
  fixed. Select a scope from task and data semantics, not from the resulting
  answer.

## Model Comparison

- Compare metrics only across compatible response definitions, likelihoods,
  transformations, and effective row sets.
- Confirm each formula, basis, parameter count, observation count, and metric
  convention that affects the comparison.
- For likelihood-derived criteria such as AIC, do not compare values from
  incompatible likelihoods or differently scoped data.
- Keep event/reference classes explicit for binary or categorical models before
  interpreting probabilities or coefficient signs.

## Evaluation And Optimization

- Use the domain specified by the task. Otherwise use the valid observed range
  after the accepted row-scope decision; do not extrapolate silently.
- Distinguish an optimum's location from the fitted response at that location.
- Extract the requested value from the accepted fitted result, not from a
  different empirical summary or a refitted replacement.

Before finalizing, verify that the actual fitted rows, model, metric, domain,
and extracted quantity match these decisions.
