# Task Authoring Guide

Each task should represent one stable biomedical objective that survives across prompt variants and environments.

## Required Task Concepts

Every v0.3 task should define:

- task identity and domain
- scientist-help band
- Galaxy complexity band
- required final artifact contract
- required step graph
- preprocessing requirements
- parameter targets
- acceptable tool classes
- acceptable solution families
- human-baseline protocol
- confidence query policy
- hidden evaluation contract

## Complexity Guidance

Complexity should reflect:

- number of required steps
- number of critical decision points
- preprocessing burden
- parameter sensitivity
- likelihood of retries or adaptation
- amount of interpretation required

## Authoring Rules

- keep the task constant across prompt variants
- do not hide required outputs only in the evaluator if they materially change the task
- define acceptable alternative scientific solutions where justified
- make Galaxy-operational expectations explicit enough to score them fairly
