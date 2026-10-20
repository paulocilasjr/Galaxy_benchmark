#!/usr/bin/env python3
"""MCP tools for exact Galaxy schema inspection and submit-then-wait execution."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tarfile
import time
import zipfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Literal, Mapping, Sequence

from galaxy_wait_mcp import (
    _extract_dataset_refs,
    _append_jsonl,
    _next_evidence_directory,
    _read_api_key,
    _redact,
    _resolve_evidence_directory,
    _write_json,
    wait_for_jobs,
)


# Legacy Galaxy tool IDs may contain internal spaces (for example,
# ``Convert characters1``). They are opaque API identifiers, not shell input.
TOOL_ID_PATTERN = re.compile(r"^[^\x00-\x1f\x7f]{1,2048}$")
HISTORY_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,256}$")
DATASET_ID_PATTERN = HISTORY_ID_PATTERN
MAX_SCHEMA_FIELDS = 200
MAX_ERROR_CHARS = 2000
MAX_SEARCH_QUERY_CHARS = 200
MAX_SEARCH_RESULTS = 10
RETURN_ALL_SEARCH_MATCHES = 20
MAX_ARCHIVE_SAMPLE = 20
MAX_HISTORY_RESULTS = 50
MAX_DATASET_PEEK_CHARS = 12_000
MAX_INLINE_OUTPUT_BYTES = 64 * 1024
MAX_INLINE_OUTPUT_TOTAL_BYTES = 128 * 1024
MAX_INLINE_OUTPUTS = 12
MAX_REPLY_TEXT_BYTES = 4096
MAX_REPLY_TEXT_TOTAL_BYTES = 8192
_SCHEMA_REPLIES: dict[tuple[str, ...], tuple[str, str]] = {}
_OUTPUT_REPLIES: dict[tuple[str, ...], tuple[str, str]] = {}
MAX_UDT_WORKSPACE_INPUTS = 32
STAGED_DATASET_FAILURE_STATES = frozenset(
    {
        "cancelled",
        "deleted",
        "discarded",
        "error",
        "failed",
        "failed_metadata",
        "paused",
        "stopped",
    }
)
COMPRESSED_TEXT_TYPES_BY_SUFFIX = {
    ".bed.gz": "bed",
    ".bedgraph.gz": "bedgraph",
    ".csv.gz": "csv",
    ".fa.gz": "fasta",
    ".fasta.gz": "fasta",
    ".fna.gz": "fasta",
    ".gff.gz": "gff",
    ".gff3.gz": "gff3",
    ".gtf.gz": "gtf",
    ".mtx.gz": "mtx",
    ".tabular.gz": "tabular",
    ".tagalign.gz": "bed",
    ".tsv.gz": "tabular",
    ".txt.gz": "txt",
    ".wig.gz": "wig",
}
CAPABILITY_QUERY_STOPWORDS = {
    "analysis",
    "data",
    "dataset",
    "file",
    "files",
    "galaxy",
    "input",
    "output",
    "tool",
}
METRIC_QUERY_TERMS = {
    "coefficient",
    "correlation",
    "count",
    "distance",
    "length",
    "likelihood",
    "mean",
    "median",
    "metric",
    "metrics",
    "probability",
    "rate",
    "ratio",
    "score",
    "statistic",
    "statistics",
    "variance",
}
SEARCH_LEXICAL_STOPWORDS = CAPABILITY_QUERY_STOPWORDS | {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "using",
    "with",
}


def _validate_identifier(value: str, *, label: str, pattern: re.Pattern[str]) -> str:
    normalized = str(value)
    if not pattern.fullmatch(normalized):
        raise ValueError(f"invalid {label}: {normalized!r}")
    return normalized


def _meaningful_error(value: Any) -> bool:
    if value in (None, "", False, [], {}):
        return False
    if isinstance(value, Mapping):
        return any(_meaningful_error(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_meaningful_error(item) for item in value)
    return True


def _scalar(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return None


def _options_summary(options: Any, limit: int = 20) -> dict[str, Any] | None:
    if not isinstance(options, list):
        return None
    values: list[dict[str, Any]] = []
    for option in options[:limit]:
        if isinstance(option, Mapping):
            values.append(
                {
                    "label": option.get("name") or option.get("label"),
                    "value": option.get("value"),
                }
            )
        elif isinstance(option, (list, tuple)):
            values.append(
                {
                    "label": option[0] if option else None,
                    "value": option[1] if len(option) > 1 else None,
                }
            )
        else:
            values.append({"label": str(option), "value": option})
    return {
        "count": len(options),
        "sample": values,
        "truncated": len(options) > limit,
    }


def _walk_inputs(
    nodes: Any,
    *,
    prefix: str = "",
    active_when: Sequence[dict[str, Any]] = (),
) -> list[dict[str, Any]]:
    if not isinstance(nodes, list):
        return []

    rows: list[dict[str, Any]] = []
    for node in nodes:
        if not isinstance(node, Mapping):
            continue
        name = str(node.get("name") or "")
        path = "|".join(part for part in (prefix, name) if part)
        kind = node.get("type")
        if kind:
            row: dict[str, Any] = {
                "active_when": list(active_when),
                "label": node.get("label"),
                "optional": node.get("optional"),
                "path": path,
                "type": kind,
                "value": _scalar(node.get("value")),
            }
            options = _options_summary(node.get("options"))
            if options is not None:
                row["options"] = options
            if kind in {"data", "data_collection"}:
                row["extensions"] = node.get("extensions") or node.get("edam")
            rows.append(row)

        controller_path = path
        test_param = node.get("test_param")
        if kind == "conditional" and isinstance(test_param, Mapping):
            test_name = str(test_param.get("name") or "")
            controller_path = "|".join(
                part for part in (path, test_name) if part
            )
            selector: dict[str, Any] = {
                "active_when": list(active_when),
                "conditional_path": path,
                "label": test_param.get("label"),
                "optional": test_param.get("optional"),
                "path": controller_path,
                "type": test_param.get("type") or "select",
                "value": _scalar(test_param.get("value")),
            }
            options = _options_summary(test_param.get("options"))
            if options is not None:
                selector["options"] = options
            rows.append(selector)

        rows.extend(
            _walk_inputs(
                node.get("inputs"),
                prefix=path,
                active_when=active_when,
            )
        )
        cases = node.get("cases")
        if isinstance(cases, list):
            for case in cases:
                if not isinstance(case, Mapping):
                    continue
                case_value = (
                    case.get("value")
                    if "value" in case
                    else case.get("case_value", case.get("name"))
                )
                condition = {"controller": controller_path, "value": case_value}
                rows.extend(
                    _walk_inputs(
                        case.get("inputs"),
                        prefix=path,
                        active_when=(*active_when, condition),
                    )
                )
    return rows


def _selector_summary(fields: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    selectors: list[dict[str, Any]] = []
    for field in fields:
        conditional_path = field.get("conditional_path")
        if not conditional_path:
            continue
        selectors.append(
            {
                "active_when": field.get("active_when") or [],
                "conditional_path": conditional_path,
                "default": field.get("value"),
                "label": field.get("label"),
                "options": field.get("options"),
                "path": field.get("path"),
            }
        )
    return selectors


def _selected_fields(
    fields: Sequence[Mapping[str, Any]],
    selector_values: Mapping[str, Any],
) -> tuple[list[Mapping[str, Any]], list[str]]:
    selected: list[Mapping[str, Any]] = []
    unresolved: set[str] = set()
    for field in fields:
        active = True
        for condition in field.get("active_when") or []:
            controller = str(condition.get("controller") or "")
            if controller not in selector_values:
                unresolved.add(controller)
                continue
            if selector_values[controller] != condition.get("value"):
                active = False
                break
        if active:
            selected.append(field)
    return selected, sorted(item for item in unresolved if item)


def _compact_outputs(outputs: Any) -> list[dict[str, Any]]:
    if not isinstance(outputs, list):
        return []
    compact: list[dict[str, Any]] = []
    for output in outputs:
        if not isinstance(output, Mapping):
            continue
        compact.append(
            {
                "format": output.get("format") or output.get("format_source"),
                "label": output.get("label"),
                "name": output.get("name"),
            }
        )
    return compact


def _filter_fields(
    fields: Sequence[Mapping[str, Any]],
    terms: Sequence[str],
) -> list[Mapping[str, Any]]:
    normalized = [term.lower() for term in terms if term.strip()]
    if not normalized:
        return list(fields)
    return [
        field
        for field in fields
        if any(term in json.dumps(field, sort_keys=True).lower() for term in normalized)
    ]


def _normalized_search_text(value: Any) -> str:
    return " ".join(re.findall(r"\w+", str(value or "").casefold()))


def _is_hidden_tool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().casefold() in {"1", "true", "yes"}


def _is_current_tool_version(tool: Mapping[str, Any]) -> bool:
    versions = tool.get("versions")
    if not isinstance(versions, list) or not versions:
        return True
    version = str(tool.get("version") or "")
    return not version or version == str(versions[-1])


def _tool_search_score(tool: Mapping[str, Any], query: str) -> int:
    query_tokens = set(query.split())
    name = _normalized_search_text(tool.get("name"))
    tool_id = _normalized_search_text(tool.get("id"))
    description = _normalized_search_text(tool.get("description"))
    section = _normalized_search_text(tool.get("panel_section_name"))
    haystack = " ".join((name, tool_id, description, section))
    haystack_tokens = set(haystack.split())

    score = 0
    if query == name:
        score = max(score, 1000)
    if query == tool_id:
        score = max(score, 950)
    if name.startswith(query):
        score = max(score, 850)
    if query in name:
        score = max(score, 800)
    if query in tool_id:
        score = max(score, 700)
    if query_tokens and query_tokens <= set(name.split()):
        score = max(score, 650)
    if query_tokens and query_tokens <= haystack_tokens:
        score = max(score, 500)
    score += 40 * len(query_tokens & haystack_tokens)

    return score


def _search_lexical_tokens(value: str) -> list[str]:
    return [
        token
        for token in _normalized_search_text(value).split()
        if token not in SEARCH_LEXICAL_STOPWORDS and not token.isdigit()
    ]


def _tool_search_confidence(tool: Mapping[str, Any], query: str) -> str | None:
    """Classify only reproducible name/ID matches as high confidence."""

    name = _normalized_search_text(tool.get("name"))
    tool_id = _normalized_search_text(tool.get("id"))
    if query == name or query == tool_id:
        return "exact"

    query_tokens = set(_search_lexical_tokens(query))
    name_tokens = set(_search_lexical_tokens(name))
    id_tokens = set(_search_lexical_tokens(tool_id))
    if len(query_tokens) >= 2 and (query in name or query in tool_id):
        return "exact"
    if len(name_tokens) >= 2 and name in query:
        return "strong"

    for identity_tokens in (name_tokens, id_tokens):
        overlap = query_tokens & identity_tokens
        if len(overlap) < 2:
            continue
        query_coverage = len(overlap) / len(query_tokens) if query_tokens else 0
        identity_coverage = (
            len(overlap) / len(identity_tokens) if identity_tokens else 0
        )
        if query_coverage >= 0.5 or identity_coverage >= 0.5:
            return "strong"
    return None


def _tool_query_identity_terms(tool: Mapping[str, Any], query: str) -> set[str]:
    identity = set(
        _search_lexical_tokens(
            f"{tool.get('name') or ''} {tool.get('id') or ''}"
        )
    )
    return identity & set(_search_lexical_tokens(query))


def _select_search_results(
    ranked: Sequence[tuple[int, Mapping[str, Any], str | None]],
    *,
    query: str,
    supplemental_limit: int,
) -> tuple[list[tuple[int, Mapping[str, Any], str | None]], str, int]:
    high_confidence = [
        item
        for item in ranked
        if _tool_search_confidence(item[1], query) is not None
    ]
    if len(ranked) <= RETURN_ALL_SEARCH_MATCHES:
        return list(ranked), "all_matches", len(high_confidence)

    selected = list(high_confidence)
    selected_ids = {str(item[1].get("id") or "") for item in selected}
    remaining = [
        item
        for item in ranked
        if str(item[1].get("id") or "") not in selected_ids
    ]
    supplemental: list[tuple[int, Mapping[str, Any], str | None]] = []
    query_terms = list(dict.fromkeys(_search_lexical_tokens(query)))

    # Preserve at least one candidate for each query concept before filling by
    # global rank. This prevents one broad term from occupying every result.
    for term in query_terms:
        if len(supplemental) >= supplemental_limit:
            break
        candidate = next(
            (
                item
                for item in remaining
                if item not in supplemental
                and term in _tool_query_identity_terms(item[1], query)
            ),
            None,
        )
        if candidate is not None:
            supplemental.append(candidate)

    for item in remaining:
        if len(supplemental) >= supplemental_limit:
            break
        if item not in supplemental:
            supplemental.append(item)

    selected.extend(supplemental)
    selected.sort(
        key=lambda item: (
            -item[0],
            str(item[1].get("name") or "").casefold(),
            str(item[1].get("id") or "").casefold(),
        )
    )
    return selected, "high_confidence_plus_diverse", len(high_confidence)


def _capability_probe_terms(
    query: str,
    tools: Sequence[Mapping[str, Any]],
    *,
    limit: int = 2,
) -> list[str]:
    """Choose rare query terms for Galaxy's parameter/help-aware ``q`` search."""

    candidates = []
    seen: set[str] = set()
    for token in query.split():
        if (
            token in seen
            or token in CAPABILITY_QUERY_STOPWORDS
            or len(token) < 4
            or token.isdigit()
        ):
            continue
        seen.add(token)
        candidates.append(token)
    if not candidates:
        return []

    documents: list[set[str]] = []
    for tool in tools:
        text = _normalized_search_text(
            " ".join(
                str(tool.get(key) or "")
                for key in ("name", "id", "description", "panel_section_name")
            )
        )
        tokens = set(text.split())
        documents.append(tokens)

    probes: list[str] = []
    has_metric_signal = any(
        token in METRIC_QUERY_TERMS or token.endswith("ness")
        for token in candidates
    )
    if has_metric_signal:
        context_candidates = [
            token
            for token in candidates
            if token not in METRIC_QUERY_TERMS and not token.endswith("ness")
        ]
        metric_context_counts = {
            token: sum(
                token in document
                and bool({"metric", "metrics"} & document)
                for document in documents
            )
            for token in context_candidates
        }
        positive_contexts = [
            token for token in context_candidates if metric_context_counts[token] > 0
        ]
        if positive_contexts:
            context = min(
                positive_contexts,
                key=lambda token: (
                    metric_context_counts[token],
                    -len(token),
                    context_candidates.index(token),
                ),
            )
            probes.append(f"{context} metrics")

    frequencies = Counter()
    for tokens in documents:
        for candidate in candidates:
            if candidate in tokens:
                frequencies[candidate] += 1
    rare_terms = sorted(
        candidates,
        key=lambda token: (frequencies[token], -len(token), candidates.index(token)),
    )
    for token in rare_terms:
        if len(probes) >= limit:
            break
        if token not in probes:
            probes.append(token)
    return probes[:limit]


def search_tool_list(
    *,
    query: str,
    fetch_tools: Callable[[], Sequence[Mapping[str, Any]]],
    workspace_root: Path,
    limit: int = 10,
    evidence_directory: str = "run_trace/galaxy_tool_search",
    fetch_capability_ids: Callable[[str], Sequence[str]] | None = None,
    secrets: Sequence[str] = (),
) -> dict[str, Any]:
    """Search the live Galaxy tool list without selecting a scientific route."""

    raw_query = str(query).strip()
    normalized_query = _normalized_search_text(raw_query)
    if not normalized_query:
        raise ValueError("query must contain at least one letter or number")
    if len(raw_query) > MAX_SEARCH_QUERY_CHARS:
        raise ValueError(
            f"query must contain at most {MAX_SEARCH_QUERY_CHARS} characters"
        )
    if not 1 <= limit <= MAX_SEARCH_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_SEARCH_RESULTS}")

    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    _write_json(
        evidence_path / "request.json",
        _redact({"limit": limit, "query": raw_query}, secrets),
    )
    try:
        raw_tools = list(fetch_tools())
    except Exception as exc:
        error = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
        _write_json(evidence_path / "search_error.json", {"error": error})
        summary = {
            "evidence_directory": evidence_directory,
            "error": error,
            "status": "failed",
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    tools = [dict(tool) for tool in raw_tools if isinstance(tool, Mapping)]
    redacted_tools = _redact(tools, secrets)
    _write_json(evidence_path / "tools_response.json", redacted_tools)

    capability_hits: dict[str, tuple[str, int]] = {}
    capability_search: dict[str, Any] = {"probes": [], "errors": {}}
    if fetch_capability_ids is not None:
        for probe in _capability_probe_terms(normalized_query, tools):
            try:
                ids = [str(item) for item in fetch_capability_ids(probe)]
            except Exception as exc:
                capability_search["errors"][probe] = str(
                    _redact(str(exc), secrets)
                )[-MAX_ERROR_CHARS:]
                continue
            capability_search["probes"].append(
                {"query": probe, "result_count": len(ids), "tool_ids": ids}
            )
            for rank, tool_id in enumerate(ids):
                capability_hits.setdefault(tool_id, (probe, rank))
            if ids:
                break
    _write_json(evidence_path / "capability_search.json", capability_search)

    ranked: list[tuple[int, Mapping[str, Any], str | None]] = []
    current_count = 0
    for tool in redacted_tools:
        if _is_hidden_tool(tool.get("hidden")) or not _is_current_tool_version(tool):
            continue
        current_count += 1
        capability_hit = capability_hits.get(str(tool.get("id") or ""))
        score = _tool_search_score(tool, normalized_query)
        if capability_hit is not None:
            score = max(score, 900 - min(capability_hit[1], 200))
        if score > 0:
            ranked.append((score, tool, capability_hit[0] if capability_hit else None))
    ranked.sort(
        key=lambda item: (
            -item[0],
            str(item[1].get("name") or "").casefold(),
            str(item[1].get("id") or "").casefold(),
        )
    )

    ranked_evidence = []
    for score, tool, capability_match in ranked:
        ranked_evidence.append(
            {
                "capability_match": capability_match,
                "confidence": _tool_search_confidence(tool, normalized_query),
                "matched_query_terms": sorted(
                    _tool_query_identity_terms(tool, normalized_query)
                ),
                "name": tool.get("name"),
                "panel_section": tool.get("panel_section_name")
                or tool.get("panel_section_id"),
                "score": score,
                "tool_id": tool.get("id"),
                "version": tool.get("version"),
            }
        )
    _write_json(evidence_path / "ranked_matches.json", ranked_evidence)

    selected, selection_mode, high_confidence_count = _select_search_results(
        ranked,
        query=normalized_query,
        supplemental_limit=limit,
    )
    results = []
    for _score, tool, capability_match in selected:
        result = {
            "name": tool.get("name"),
            "panel_section": tool.get("panel_section_name")
            or tool.get("panel_section_id"),
            "tool_id": tool.get("id"),
            "version": tool.get("version"),
        }
        if capability_match:
            result["capability_matches"] = [capability_match]
        results.append(result)
    summary = {
        "capability_probe_count": len(capability_search["probes"]),
        "capability_probes": [
            item["query"] for item in capability_search["probes"]
        ],
        "evidence_directory": evidence_directory,
        "live_tool_count": len(tools),
        "matching_tool_count": len(ranked),
        "result_count": len(results),
        "results": results,
        "high_confidence_count": high_confidence_count,
        "searchable_current_tool_count": current_count,
        "selection_mode": selection_mode,
        "status": "ok",
        "truncated": len(selected) < len(ranked),
    }
    _write_json(evidence_path / "summary.json", summary)
    return summary


def inspect_tool_schema(
    *,
    tool_id: str,
    build_tool: Callable[[str, str | None], Mapping[str, Any]],
    workspace_root: Path,
    show_tool: Callable[[str], Mapping[str, Any]] | None = None,
    history_id: str | None = None,
    field_filter: Sequence[str] = (),
    evidence_directory: str = "run_trace/galaxy_tool_schema",
    field_limit: int = 80,
    selector_values: Mapping[str, Any] | None = None,
    secrets: Sequence[str] = (),
    refresh: bool = False,
) -> dict[str, Any]:
    """Inspect one agent-selected Galaxy tool without searching or choosing a route."""

    tool_id = _validate_identifier(tool_id, label="tool ID", pattern=TOOL_ID_PATTERN)
    if history_id is not None:
        history_id = _validate_identifier(
            history_id,
            label="history ID",
            pattern=HISTORY_ID_PATTERN,
        )
    if not 1 <= field_limit <= MAX_SCHEMA_FIELDS:
        raise ValueError(f"field_limit must be between 1 and {MAX_SCHEMA_FIELDS}")

    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    _write_json(
        evidence_path / "request.json",
        _redact(
            {
                "field_filter": list(field_filter),
                "field_limit": field_limit,
                "history_id": history_id,
                "selector_values": dict(selector_values or {}),
                "tool_id": tool_id,
            },
            secrets,
        ),
    )

    history_context = "requested" if history_id is not None else "not_requested"
    try:
        response = _redact(dict(build_tool(tool_id, history_id)), secrets)
    except Exception as exc:
        error = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
        _write_json(evidence_path / "build_error.json", {"error": error})
        if history_id is None:
            summary = {
                "evidence_directory": evidence_directory,
                "error": error,
                "status": "failed",
                "tool_id": tool_id,
            }
            _write_json(evidence_path / "summary.json", summary)
            return summary
        try:
            response = _redact(dict(build_tool(tool_id, None)), secrets)
            history_context = "omitted_after_history_build_error"
        except Exception as fallback_exc:
            fallback_error = str(_redact(str(fallback_exc), secrets))[
                -MAX_ERROR_CHARS:
            ]
            _write_json(
                evidence_path / "fallback_build_error.json",
                {"error": fallback_error},
            )
            summary = {
                "evidence_directory": evidence_directory,
                "error": fallback_error,
                "history_error": error,
                "status": "failed",
                "tool_id": tool_id,
            }
            _write_json(evidence_path / "summary.json", summary)
            return summary

    _write_json(evidence_path / "build_response.json", response)
    fields = _walk_inputs(response.get("inputs"))
    _write_json(evidence_path / "fields.json", fields)
    selectors = _selector_summary(fields)
    candidate_fields: Sequence[Mapping[str, Any]] = fields
    unresolved_selectors: list[str] = []
    if selector_values:
        candidate_fields, unresolved_selectors = _selected_fields(
            fields,
            selector_values,
        )
    matching_fields = _filter_fields(candidate_fields, field_filter)
    displayed = matching_fields[:field_limit]
    outputs = _compact_outputs(response.get("outputs"))
    outputs_source = "build"
    if not outputs and show_tool is not None:
        try:
            tool_response = _redact(dict(show_tool(tool_id)), secrets)
            _write_json(evidence_path / "tool_response.json", tool_response)
            outputs = _compact_outputs(tool_response.get("outputs"))
            outputs_source = "show_tool"
        except Exception as exc:
            error = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
            _write_json(evidence_path / "tool_response_error.json", {"error": error})
            outputs_source = "unavailable"
    repeat_paths = {field["path"] for field in fields if field.get("type") == "repeat"}
    compact_fields = []
    template = {}
    effective_selectors = {selector["path"]: selector.get("default") for selector in selectors}
    effective_selectors.update(selector_values or {})
    for field in displayed:
        compact = {key: value for key, value in field.items()
                   if value is not None and value != []}
        parts = field["path"].split("|")
        submission_path = "|".join(
            f"{part}_0" if "|".join(parts[:index + 1]) in repeat_paths else part
            for index, part in enumerate(parts)
        )
        if field["type"] not in {"repeat", "section", "conditional"}:
            if submission_path != field["path"]:
                compact["submission_path"] = submission_path
            if all(str(effective_selectors.get(rule["controller"])) == str(rule["value"])
                   for rule in field.get("active_when", [])):
                default = field.get("value")
                template[submission_path] = (
                    {"src": "hdca" if field["type"] == "data_collection" else "hda", "id": "<dataset-id>"}
                    if field["type"] in {"data", "data_collection"}
                    else default if default is not None else "<value>"
                )
        compact_fields.append(compact)
    summary = {
        "evidence_directory": evidence_directory,
        "field_count": len(fields),
        "field_filter": list(field_filter),
        "fields": displayed,
        "history_context": history_context,
        "matching_field_count": len(matching_fields),
        "name": response.get("name"),
        "outputs": outputs,
        "outputs_source": outputs_source,
        "recommended_input_format": "21.01",
        "submission_formats": {
            "21.01": "Nested objects for sections/conditionals; arrays of objects for repeats. Include the conditional controller inside its object.",
            "legacy": "Flat keys: section|field, conditional|controller, repeat_0|field (then repeat_1|field). Use input_format=legacy with these paths.",
            "dataset": {"src": "hda", "id": "<dataset-id>"},
            "collection": {"src": "hdca", "id": "<collection-id>"},
            "auto": "Chooses legacy when a top-level key contains |, otherwise 21.01. Do not mix formats.",
        },
        "selectors": selectors,
        "selector_values": dict(selector_values or {}),
        "status": "ok",
        "tool_id": tool_id,
        "truncated": len(matching_fields) > len(displayed),
        "unresolved_selectors": unresolved_selectors,
        "version": response.get("version"),
    }
    _write_json(evidence_path / "summary.json", summary)
    displayed_paths = {field["path"] for field in displayed}
    compact_selectors = [{key: value for key, value in selector.items()
                          if value is not None and value != []
                          and not (key in {"label", "options", "conditional_path"}
                                   and selector["path"] in displayed_paths)}
                         for selector in selectors]
    model_summary = {**{key: value for key, value in summary.items()
                        if key not in {"submission_formats", "field_filter", "selector_values"}},
                     "fields": compact_fields, "selectors": compact_selectors,
                     "recommended_input_format": "legacy",
                     "input_template": {"input_format": "legacy", "tool_inputs": template},
                     "template_note": "Live defaults, not task settings. Replace placeholders. Repeat _0 is the first instance. This template covers only displayed fields."}
    # Cache what was shown, not live API data or history-specific choices.
    key = (
        str(workspace_root.resolve()), os.environ.get("GALAXY_URL", "https://usegalaxy.org"),
        history_id or "", tool_id,
        json.dumps([field_filter, field_limit, selector_values], sort_keys=True),
    )
    digest = hashlib.sha256(json.dumps(
        {k: v for k, v in model_summary.items() if k != "evidence_directory"},
        sort_keys=True,
    ).encode()).hexdigest()
    previous = _SCHEMA_REPLIES.get(key)
    reply = model_summary
    if not refresh and previous and previous[0] == digest:
        reply = {
            "status": "ok", "tool_id": tool_id, "version": summary["version"],
            "unchanged": True, "evidence_directory": evidence_directory,
            "previous_evidence_directory": previous[1],
            "reread": "Set refresh=true to receive the schema again.",
        }
    else:
        _SCHEMA_REPLIES[key] = (digest, evidence_directory)
    _write_json(evidence_path / "model_response.json", reply)
    return reply


def _job_ids_from_submission(response: Mapping[str, Any]) -> list[str]:
    job_ids: list[str] = []
    for job in response.get("jobs") or []:
        if isinstance(job, Mapping) and isinstance(job.get("id"), str):
            if job["id"] not in job_ids:
                job_ids.append(job["id"])
    return job_ids


def _history_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        history_id = value.get("history_id")
        if isinstance(history_id, str):
            found.add(history_id)
        for item in value.values():
            found.update(_history_ids(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.update(_history_ids(item))
    return found


def _select_input_format(requested: str, tool_inputs: Mapping[str, Any]) -> str:
    if requested in {"legacy", "21.01"}:
        return requested
    if requested != "auto":
        raise ValueError("input_format must be 'auto', 'legacy', or '21.01'")
    if any("|" in str(key) for key in tool_inputs):
        return "legacy"
    return "21.01"


def _is_dataset_ref(value: Any) -> bool:
    return (
        isinstance(value, Mapping)
        and value.get("src") in {"hda", "hdca", "ldda"}
        and isinstance(value.get("id"), str)
    )


def _decode_job_param(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _flatten_non_dataset_parameters(
    value: Any,
    *,
    prefix: tuple[str, ...] = (),
) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    if _is_dataset_ref(value):
        return flattened
    if isinstance(value, Mapping):
        for raw_key, item in value.items():
            key = str(raw_key)
            if key.startswith("__"):
                continue
            parts = tuple(part for part in key.split("|") if part)
            flattened.update(
                _flatten_non_dataset_parameters(item, prefix=(*prefix, *parts))
            )
        return flattened
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            flattened.update(
                _flatten_non_dataset_parameters(item, prefix=(*prefix, str(index)))
            )
        return flattened
    if prefix:
        flattened["|".join(prefix)] = value
    return flattened


def _decoded_job_params(job: Mapping[str, Any]) -> dict[str, Any]:
    raw_params = job.get("params")
    if not isinstance(raw_params, Mapping):
        return {}
    return {
        str(key): _decode_job_param(value)
        for key, value in raw_params.items()
        if not str(key).startswith("__")
    }


def _canonical_parameters(value: Any, repeat_paths: set[str]) -> dict[str, Any]:
    """Normalize only repeat aliases established by the live tool schema."""
    result: dict[str, Any] = {}
    for path, item in _flatten_non_dataset_parameters(value).items():
        parts: list[str] = []
        schema_parts: list[str] = []
        for part in path.split("|"):
            match = re.fullmatch(r"(.+)_(\d+)", part)
            if match and "|".join([*schema_parts, match[1]]) in repeat_paths:
                parts.extend(match.groups())
                schema_parts.append(match[1])
            else:
                parts.append(part)
                if not (part.isdigit() and "|".join(schema_parts) in repeat_paths):
                    schema_parts.append(part)
        canonical = "|".join(parts)
        if canonical in result:
            raise ValueError(f"ambiguous parameter aliases: {canonical}")
        result[canonical] = item
    return result


def _legacy_build_inputs(value: Mapping[str, Any], fields: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Convert transport syntax only; scalar/JSON/data values remain untouched."""
    kinds = {field["path"]: field["type"] for field in fields}
    result: dict[str, Any] = {}

    def walk(items: Mapping[str, Any], schema_prefix: str = "", legacy_prefix: str = "") -> None:
        for name, item in items.items():
            if name.startswith("__"):
                continue
            schema_path = "|".join(p for p in (schema_prefix, name) if p)
            legacy_path = "|".join(p for p in (legacy_prefix, name) if p)
            kind = kinds.get(schema_path)
            if kind in {"conditional", "section"} and isinstance(item, Mapping):
                walk(item, schema_path, legacy_path)
            elif kind == "repeat" and isinstance(item, list):
                for index, child in enumerate(item):
                    if not isinstance(child, Mapping):
                        raise ValueError(f"repeat {schema_path} requires objects")
                    walk(child, schema_path, f"{legacy_path}_{index}")
            else:
                if legacy_path in result:
                    raise ValueError(f"ambiguous build parameter: {legacy_path}")
                result[legacy_path] = item

    walk(value)
    return result


def _saved_schema_fields(workspace_root: Path, tool_id: str, history_id: str) -> list[dict[str, Any]]:
    for directory in sorted((workspace_root / "run_trace").glob("galaxy_tool_schema*"),
                            key=lambda path: path.stat().st_mtime, reverse=True):
        if not (directory / "fields.json").is_file() or not (directory / "request.json").is_file():
            continue
        request = json.loads((directory / "request.json").read_text())
        if request.get("tool_id") == tool_id and request.get("history_id") in (None, history_id):
            return json.loads((directory / "fields.json").read_text())
    return []


def _decimal_value(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    if not isinstance(value, (str, int, float, Decimal)):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


def _parameter_values_equal(expected: Any, resolved: Any) -> bool:
    if expected == resolved:
        return True
    if expected is None and isinstance(resolved, str) and not resolved.strip():
        return True
    if resolved is None and isinstance(expected, str) and not expected.strip():
        return True
    if isinstance(expected, bool) and isinstance(resolved, str):
        return resolved.strip().lower() == str(expected).lower()
    if isinstance(resolved, bool) and isinstance(expected, str):
        return expected.strip().lower() == str(resolved).lower()
    expected_number = _decimal_value(expected)
    resolved_number = _decimal_value(resolved)
    return (
        expected_number is not None
        and resolved_number is not None
        and expected_number == resolved_number
    )


def _validation_parameter_summary(
    tool_inputs: Mapping[str, Any],
    validation: Mapping[str, Any],
    repeat_paths: set[str] | None = None,
) -> dict[str, Any]:
    """Compare explicit scalar inputs with Galaxy's normalized build state."""

    repeat_paths = repeat_paths or {field["path"] for field in _walk_inputs(validation.get("inputs"))
                                    if field.get("type") == "repeat"}
    expected = _canonical_parameters(tool_inputs, repeat_paths)
    if not expected:
        return {
            "checked_parameter_count": 0,
            "mismatches": [],
            "missing_paths": [],
            "status": "no_explicit_non_dataset_parameters",
        }
    state_inputs = validation.get("state_inputs")
    if not isinstance(state_inputs, Mapping):
        return {
            "checked_parameter_count": len(expected),
            "mismatches": [],
            "missing_paths": sorted(expected),
            "status": "not_comparable",
        }
    resolved = _canonical_parameters(state_inputs, repeat_paths)
    missing = sorted(path for path in expected if path not in resolved)
    mismatches = [
        {
            "expected": expected[path],
            "path": path,
            "resolved": resolved[path],
        }
        for path in sorted(expected.keys() & resolved.keys())
        if not _parameter_values_equal(expected[path], resolved[path])
    ]
    return {
        "checked_parameter_count": len(expected),
        "mismatches": mismatches,
        "missing_paths": missing,
        "status": "matched" if not missing and not mismatches else "mismatch",
    }


def _parameter_provenance_summary(
    tool_inputs: Mapping[str, Any],
    jobs: Sequence[Mapping[str, Any]],
    repeat_paths: set[str] | None = None,
) -> dict[str, Any]:
    repeat_paths = repeat_paths or set()
    expected = _canonical_parameters(tool_inputs, repeat_paths)
    if not expected:
        return {
            "checked_parameter_count": 0,
            "jobs": [],
            "status": "no_explicit_non_dataset_parameters",
        }

    job_results: list[dict[str, Any]] = []
    comparable_jobs = 0
    for job in jobs:
        resolved = _canonical_parameters(_decoded_job_params(job), repeat_paths)
        if not resolved:
            job_results.append(
                {
                    "job_id": job.get("id"),
                    "missing_paths": sorted(expected),
                    "mismatches": [],
                    "status": "not_comparable",
                }
            )
            continue
        comparable_jobs += 1
        missing = sorted(path for path in expected if path not in resolved)
        mismatches = [
            {
                "expected": expected[path],
                "path": path,
                "resolved": resolved[path],
            }
            for path in sorted(expected.keys() & resolved.keys())
            if not _parameter_values_equal(expected[path], resolved[path])
        ]
        job_results.append(
            {
                "job_id": job.get("id"),
                "missing_paths": missing,
                "mismatches": mismatches,
                "status": "matched" if not missing and not mismatches else "mismatch",
            }
        )

    if any(job["status"] == "mismatch" for job in job_results):
        status = "mismatch"
    elif comparable_jobs == len(jobs) and jobs:
        status = "matched"
    else:
        status = "not_comparable"
    return {
        "checked_parameter_count": len(expected),
        "jobs": job_results,
        "status": status,
    }


def _conversion_lineage(
    *,
    intended_hda_ids: set[str],
    resolved_hda_ids: set[str],
    history_id: str,
    fetch_dataset: Callable[[str], Mapping[str, Any]] | None,
    fetch_job: Callable[[str], Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    if fetch_dataset is None or fetch_job is None:
        return []
    relationships: list[dict[str, Any]] = []
    for resolved_id in sorted(resolved_hda_ids):
        try:
            dataset = dict(fetch_dataset(resolved_id))
            creating_job_id = dataset.get("creating_job")
            if dataset.get("history_id") != history_id or not isinstance(
                creating_job_id, str
            ):
                continue
            conversion_job = dict(fetch_job(creating_job_id))
        except Exception:
            continue
        if conversion_job.get("history_id") != history_id:
            continue
        conversion_inputs = {
            ref["id"]
            for ref in _extract_dataset_refs(conversion_job.get("inputs") or {})
            if ref.get("src") == "hda"
        }
        conversion_outputs = {
            ref["id"]
            for ref in _extract_dataset_refs(conversion_job.get("outputs") or {})
            if ref.get("src") == "hda"
        }
        source_ids = sorted(intended_hda_ids & conversion_inputs)
        if source_ids and resolved_id in conversion_outputs:
            relationships.append(
                {
                    "conversion_job_id": creating_job_id,
                    "resolved_hda_id": resolved_id,
                    "source_hda_ids": source_ids,
                    "tool_id": conversion_job.get("tool_id"),
                }
            )
    return relationships


def _provenance_summary(
    tool_inputs: Mapping[str, Any],
    jobs: Sequence[Mapping[str, Any]],
    *,
    history_id: str,
    fetch_dataset: Callable[[str], Mapping[str, Any]] | None = None,
    fetch_job: Callable[[str], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    intended = _extract_dataset_refs(tool_inputs)
    resolved: list[dict[str, str]] = []
    for job in jobs:
        for ref in job.get("input_dataset_refs") or []:
            if isinstance(ref, Mapping):
                normalized = {str(key): str(value) for key, value in ref.items()}
                if normalized not in resolved:
                    resolved.append(normalized)

    intended_hdas = {ref["id"] for ref in intended if ref.get("src") == "hda"}
    resolved_hdas = {ref["id"] for ref in resolved if ref.get("src") == "hda"}
    lineage: list[dict[str, Any]] = []
    if not intended_hdas or not resolved_hdas:
        status = "not_comparable"
        missing: list[str] = []
    else:
        missing = sorted(intended_hdas - resolved_hdas)
        if missing:
            lineage = _conversion_lineage(
                intended_hda_ids=set(missing),
                resolved_hda_ids=resolved_hdas,
                history_id=history_id,
                fetch_dataset=fetch_dataset,
                fetch_job=fetch_job,
            )
            explained = {
                source_id
                for relationship in lineage
                for source_id in relationship["source_hda_ids"]
            }
            missing = sorted(set(missing) - explained)
        status = "matched" if not missing else "mismatch"
    return {
        "accepted_conversion_lineage": lineage,
        "intended_dataset_refs": intended,
        "missing_intended_hda_ids": missing,
        "resolved_dataset_refs": resolved,
        "status": status,
    }


def _unique_output_refs(refs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Missing src means hda only in this output-dataset context."""
    seen: set[tuple[str, str]] = set()
    result = []
    for ref in refs:
        if not isinstance(ref.get("id"), str):
            continue
        key = (str(ref.get("src") or "hda"), ref["id"])
        if key not in seen:
            seen.add(key)
            result.append(dict(ref))
    return result


def compact_execution_reply(
    summary: Mapping[str, Any], *, history_id: str, workspace_root: Path,
) -> dict[str, Any]:
    """Keep full saved evidence; shorten only successful model-facing replies."""
    reply = dict(summary)
    if summary.get("status") != "ok" or not isinstance(summary.get("evidence_directory"), str):
        return reply
    reply["history_id"] = history_id
    reply["jobs"] = [
        {key: job[key] for key in ("id", "state", "tool_id") if key in job}
        for job in summary.get("jobs", [])
    ]
    reply["checks"] = {
        key: reply.pop(key)["status"]
        for key in ("provenance", "parameter_provenance", "output_verification", "output_collection_verification")
        if isinstance(reply.get(key), Mapping) and "status" in reply[key]
    }
    for key in ("history_mismatch", "failure_summary"):
        if not reply.get(key):
            reply.pop(key, None)
    reply["output_dataset_refs"] = _unique_output_refs(summary.get("output_dataset_refs", []))
    full_record = f"{summary['evidence_directory']}/summary.json"
    reply["full_record"] = full_record
    inline = []
    remaining_bytes = MAX_REPLY_TEXT_TOTAL_BYTES
    for output in summary.get("inline_outputs", []):
        record = dict(output)
        content = record.get("content")
        if isinstance(content, str):
            key = (
                str(workspace_root.resolve()), os.environ.get("GALAXY_URL", "https://usegalaxy.org"),
                history_id, str(record.get("src") or "hda"), str(record["dataset_id"]),
            )
            digest = hashlib.sha256(content.encode()).hexdigest()
            previous = _OUTPUT_REPLIES.get(key)
            if previous and previous[0] == digest:
                record.pop("content")
                record.update(status="unchanged", previous_full_record=previous[1])
            else:
                limit = min(MAX_REPLY_TEXT_BYTES, remaining_bytes)
                if len(content.encode()) > limit:
                    record.pop("content")
                    record.update(
                        status="preview" if limit else "saved_only", preview_truncated=True,
                        preview=content.encode()[:limit].decode("utf-8", errors="ignore"),
                    )
                remaining_bytes -= min(len(content.encode()), limit)
                _OUTPUT_REPLIES[key] = (digest, full_record)
            record["full_record"] = full_record
        inline.append(record)
    reply["inline_outputs"] = inline
    reply["reread"] = "Read only needed fields/rows from full_record; do not resubmit the job to reread."
    _write_json(workspace_root / summary["evidence_directory"] / "model_response.json", reply)
    return reply


def _inline_output_summaries(
    *,
    output_refs: Sequence[Mapping[str, Any]],
    history_id: str,
    fetch_dataset: Callable[[str], Mapping[str, Any]] | None,
    fetch_dataset_prefix: Callable[[str, int], bytes] | None,
    evidence_path: Path,
    secrets: Sequence[str] = (),
) -> list[dict[str, Any]]:
    """Inline complete small UTF-8 outputs without turning previews into downloads."""

    if fetch_dataset is None or fetch_dataset_prefix is None:
        return []
    records: list[dict[str, Any]] = []
    remaining_bytes = MAX_INLINE_OUTPUT_TOTAL_BYTES
    output_refs = _unique_output_refs(output_refs)
    for ref in output_refs[:MAX_INLINE_OUTPUTS]:
        dataset_id = ref.get("id")
        if not isinstance(dataset_id, str):
            continue
        record: dict[str, Any] = {"dataset_id": dataset_id}
        if ref.get("src") not in (None, "hda"):
            records.append({**record, "src": ref["src"], "status": "unsupported_dataset_source"})
            continue
        try:
            dataset = dict(fetch_dataset(dataset_id))
            record.update(
                {
                    "extension": dataset.get("extension") or dataset.get("file_ext"),
                    "file_size": dataset.get("file_size"),
                    "name": dataset.get("name"),
                    "state": dataset.get("state"),
                }
            )
            observed_history_id = dataset.get("history_id")
            if observed_history_id is None:
                record["status"] = "history_unverified"
                records.append(record)
                continue
            if observed_history_id != history_id:
                record["status"] = "history_mismatch"
                records.append(record)
                continue
            if dataset.get("state") != "ok":
                record["status"] = "dataset_not_ready"
                records.append(record)
                continue
            if remaining_bytes <= 0:
                record["status"] = "total_limit_reached"
                records.append(record)
                continue
            file_size = dataset.get("file_size")
            if isinstance(file_size, (int, float)) and file_size > min(
                MAX_INLINE_OUTPUT_BYTES,
                remaining_bytes,
            ):
                record["status"] = "too_large"
                records.append(record)
                continue
            limit = min(MAX_INLINE_OUTPUT_BYTES, remaining_bytes)
            payload = fetch_dataset_prefix(dataset_id, limit + 1)
            if len(payload) > limit:
                record["status"] = "too_large"
                records.append(record)
                continue
            if b"\x00" in payload:
                record["status"] = "non_text"
                records.append(record)
                continue
            try:
                content = payload.decode("utf-8")
            except UnicodeDecodeError:
                record["status"] = "non_utf8"
                records.append(record)
                continue
            record.update(
                {
                    "content": _redact(content, secrets),
                    "content_bytes": len(payload),
                    "content_sha256": hashlib.sha256(payload).hexdigest(),
                    "status": "inlined",
                }
            )
            remaining_bytes -= len(payload)
        except Exception as exc:
            record.update(
                {
                    "error": str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:],
                    "status": "unavailable",
                }
            )
        records.append(record)

    if len(output_refs) > MAX_INLINE_OUTPUTS:
        records.append(
            {
                "omitted_output_count": len(output_refs) - MAX_INLINE_OUTPUTS,
                "status": "output_count_limit_reached",
            }
        )
    _write_json(evidence_path / "inline_outputs.json", records)
    return records


def run_tool_and_wait(
    *,
    history_id: str,
    tool_id: str,
    tool_inputs: Mapping[str, Any],
    build_tool: Callable[[str, Mapping[str, Any], str], Mapping[str, Any]],
    submit_tool: Callable[[str, str, Mapping[str, Any], str], Mapping[str, Any]],
    fetch_job: Callable[[str], Mapping[str, Any]],
    workspace_root: Path,
    fetch_dataset: Callable[[str], Mapping[str, Any]] | None = None,
    fetch_collection: Callable[[str], Mapping[str, Any]] | None = None,
    fetch_dataset_prefix: Callable[[str, int], bytes] | None = None,
    input_format: str = "auto",
    validate_before_submit: bool = True,
    timeout_seconds: float | None = None,
    start_timeout_seconds: float | None = None,
    poll_interval_seconds: float = 10.0,
    evidence_directory: str = "run_trace/galaxy_tool_run",
    secrets: Sequence[str] = (),
) -> dict[str, Any]:
    """Submit an exact agent-authored payload and wait without changing it."""

    history_id = _validate_identifier(
        history_id,
        label="history ID",
        pattern=HISTORY_ID_PATTERN,
    )
    tool_id = _validate_identifier(tool_id, label="tool ID", pattern=TOOL_ID_PATTERN)
    if not isinstance(tool_inputs, Mapping):
        raise ValueError("tool_inputs must be a JSON object")

    exact_inputs = dict(tool_inputs)
    selected_input_format = _select_input_format(input_format, exact_inputs)
    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    _write_json(
        evidence_path / "request.json",
        _redact(
            {
                "history_id": history_id,
                "input_format": input_format,
                "selected_input_format": selected_input_format,
                "tool_id": tool_id,
                "tool_inputs": exact_inputs,
                "validate_before_submit": validate_before_submit,
            },
            secrets,
        ),
    )

    schema_fields = _saved_schema_fields(workspace_root, tool_id, history_id)
    repeat_paths = {field["path"] for field in schema_fields if field.get("type") == "repeat"}
    validation_status = "skipped"
    if validate_before_submit:
        try:
            if not schema_fields:
                schema = _redact(dict(build_tool(tool_id, {}, history_id)), secrets)
                _write_json(evidence_path / "validation_schema_response.json", schema)
                schema_fields = _walk_inputs(schema.get("inputs"))
                repeat_paths = {field["path"] for field in schema_fields if field.get("type") == "repeat"}
            build_inputs = (_legacy_build_inputs(exact_inputs, schema_fields)
                            if selected_input_format == "21.01" else exact_inputs)
            _write_json(evidence_path / "validation_request.json",
                        _redact({"input_format": "legacy", "tool_inputs": build_inputs}, secrets))
            validation = _redact(
                dict(build_tool(tool_id, build_inputs, history_id)),
                secrets,
            )
            _write_json(evidence_path / "validation_response.json", validation)
            if _meaningful_error(validation.get("errors")):
                summary = {
                    "evidence_directory": evidence_directory,
                    "errors": validation.get("errors"),
                    "status": "validation_failed",
                    "submitted": False,
                    "tool_id": tool_id,
                }
                _write_json(evidence_path / "summary.json", summary)
                return summary
            validation_parameters = _validation_parameter_summary(
                exact_inputs,
                validation,
                repeat_paths,
            )
            _write_json(
                evidence_path / "validation_parameter_provenance.json",
                validation_parameters,
            )
            if validation_parameters["status"] == "mismatch":
                summary = {
                    "evidence_directory": evidence_directory,
                    "parameter_provenance": validation_parameters,
                    "status": "validation_parameter_mismatch",
                    "submitted": False,
                    "tool_id": tool_id,
                    "validation_status": "parameter_mismatch",
                }
                _write_json(evidence_path / "summary.json", summary)
                return summary
            validation_status = "passed"
        except ValueError as exc:
            summary = {"status": "validation_failed", "submitted": False,
                       "tool_id": tool_id, "error": str(_redact(str(exc), secrets)),
                       "evidence_directory": evidence_directory}
            _write_json(evidence_path / "summary.json", summary)
            return summary
        except Exception as exc:
            error = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
            _write_json(evidence_path / "validation_error.json", {"error": error})
            validation_status = "unavailable"

    try:
        submission = _redact(
            dict(
                submit_tool(
                    history_id,
                    tool_id,
                    exact_inputs,
                    selected_input_format,
                )
            ),
            secrets,
        )
    except Exception as exc:
        error = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
        _write_json(evidence_path / "submission_error.json", {"error": error})
        summary = {
            "evidence_directory": evidence_directory,
            "error": error,
            "status": "submission_failed",
            "submitted": False,
            "tool_id": tool_id,
            "selected_input_format": selected_input_format,
            "validation_status": validation_status,
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    _write_json(evidence_path / "submission_response.json", submission)
    job_ids = _job_ids_from_submission(submission)
    output_refs = _extract_dataset_refs(submission.get("outputs") or [])
    output_collection_refs = _extract_dataset_refs(
        submission.get("output_collections") or []
    )
    observed_history_ids = _history_ids(
        {
            "outputs": submission.get("outputs"),
            "output_collections": submission.get("output_collections"),
        }
    )
    history_mismatch = sorted(observed_history_ids - {history_id})

    if not job_ids:
        summary = {
            "evidence_directory": evidence_directory,
            "history_mismatch": history_mismatch,
            "output_collection_refs": output_collection_refs,
            "output_dataset_refs": output_refs,
            "status": "submission_returned_no_jobs",
            "submitted": True,
            "tool_id": tool_id,
            "selected_input_format": selected_input_format,
            "validation_status": validation_status,
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    wait_result = wait_for_jobs(
        job_ids,
        fetch_job=fetch_job,
        workspace_root=workspace_root,
        evidence_directory=f"{evidence_directory}/wait",
        timeout_seconds=timeout_seconds,
        start_timeout_seconds=start_timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
        secrets=secrets,
    )
    final_jobs_path = evidence_path / "wait" / "final_jobs.json"
    full_jobs: list[Mapping[str, Any]] = []
    if final_jobs_path.is_file():
        raw_jobs = json.loads(final_jobs_path.read_text(encoding="utf-8"))
        if isinstance(raw_jobs, Mapping):
            full_jobs = [
                job for job in raw_jobs.values() if isinstance(job, Mapping)
            ]
    provenance = _provenance_summary(
        exact_inputs,
        wait_result["jobs"],
        history_id=history_id,
        fetch_dataset=fetch_dataset,
        fetch_job=fetch_job,
    )
    parameter_provenance = _parameter_provenance_summary(exact_inputs, full_jobs, repeat_paths)
    _write_json(evidence_path / "parameter_provenance.json", parameter_provenance)
    for job in wait_result["jobs"]:
        for ref in job.get("output_dataset_refs") or []:
            if ref not in output_refs:
                output_refs.append(ref)
    status = wait_result["status"]
    elapsed_seconds = wait_result["elapsed_seconds"]
    failure_summary = wait_result["failure_summary"]
    if history_mismatch:
        status = "history_mismatch"
    elif status == "ok" and provenance["status"] == "mismatch":
        status = "provenance_mismatch"
    elif status == "ok" and parameter_provenance["status"] == "mismatch":
        status = "parameter_mismatch"

    collection_verification: dict[str, Any] | None = None
    if status == "ok" and output_collection_refs:
        if fetch_collection is None:
            status = "output_verification_unavailable"
            failure_summary = "No dataset-collection lookup was available."
        else:
            collection_verification = _wait_for_output_collections(
                history_id=history_id,
                collection_refs=output_collection_refs,
                fetch_collection=fetch_collection,
                workspace_root=workspace_root,
                evidence_directory=f"{evidence_directory}/output_collections",
                poll_interval_seconds=poll_interval_seconds,
                secrets=secrets,
            )
            elapsed_seconds += collection_verification["elapsed_seconds"]
            if collection_verification["status"] != "ok":
                status = collection_verification["status"]
                failure_summary = collection_verification["failure_summary"]
            for ref in collection_verification["dataset_refs"]:
                if ref not in output_refs:
                    output_refs.append(ref)

    output_refs = _unique_output_refs(output_refs)
    output_verification: dict[str, Any] | None = None
    if status == "ok" and output_refs:
        if fetch_dataset is None:
            status = "output_verification_unavailable"
            failure_summary = "No output dataset lookup was available."
        else:
            output_verification = _wait_for_staged_datasets(
                history_id=history_id,
                dataset_refs=output_refs,
                fetch_dataset=fetch_dataset,
                workspace_root=workspace_root,
                evidence_directory=f"{evidence_directory}/outputs",
                poll_interval_seconds=poll_interval_seconds,
                secrets=secrets,
            )
            elapsed_seconds += output_verification["elapsed_seconds"]
            if output_verification["status"] != "ok":
                status = output_verification["status"]
                failure_summary = output_verification["failure_summary"]

    inline_outputs = (
        _inline_output_summaries(
            output_refs=output_refs,
            history_id=history_id,
            fetch_dataset=fetch_dataset,
            fetch_dataset_prefix=fetch_dataset_prefix,
            evidence_path=evidence_path,
            secrets=secrets,
        )
        if status == "ok"
        else []
    )

    summary = _redact(
        {
            "elapsed_seconds": elapsed_seconds,
            "evidence_directory": evidence_directory,
            "failure_summary": failure_summary,
            "history_mismatch": history_mismatch,
            "inline_outputs": inline_outputs,
            "jobs": wait_result["jobs"],
            "output_collection_refs": output_collection_refs,
            "output_collection_verification": collection_verification,
            "output_dataset_refs": output_refs,
            "output_verification": output_verification,
            "parameter_provenance": parameter_provenance,
            "provenance": provenance,
            "selected_input_format": selected_input_format,
            "status": status,
            "submitted": True,
            "tool_id": tool_id,
            "validation_status": validation_status,
        },
        secrets,
    )
    _write_json(evidence_path / "summary.json", summary)
    return summary


def _validate_udt_representation(representation: Mapping[str, Any]) -> dict[str, Any]:
    exact = dict(representation)
    if exact.get("class") != "GalaxyUserTool":
        raise ValueError("UDT representation class must be 'GalaxyUserTool'")
    for field in ("id", "name", "version", "shell_command"):
        if not isinstance(exact.get(field), str) or not exact[field].strip():
            raise ValueError(f"UDT representation requires non-empty {field!r}")
    for field in ("inputs", "outputs"):
        if not isinstance(exact.get(field), list) or not exact[field]:
            raise ValueError(f"UDT representation requires a non-empty {field!r} list")
        names: set[str] = set()
        for item in exact[field]:
            if not isinstance(item, Mapping) or not isinstance(item.get("name"), str) or not item["name"].strip():
                raise ValueError(f"Each UDT {field} entry requires a name")
            if item["name"] in names:
                raise ValueError(f"Duplicate UDT {field} name: {item['name']!r}")
            names.add(item["name"])
    input_names = {item["name"] for item in exact["inputs"]}
    commands = [exact["shell_command"]] + [
        config.get("content", "") for config in exact.get("configfiles", [])
        if isinstance(config, Mapping)
    ]
    # ponytail: literal input references only; Galaxy validates general ECMAScript.
    for command in commands:
        if not isinstance(command, str):
            raise ValueError("UDT configfile content must be text")
        for dot_name, bracket_name in re.findall(
            r"(?<!\\)\$\(\s*inputs(?:\.([A-Za-z_$][\w$]*)|\[['\"]([^'\"]+)['\"]\])", command,
        ):
            name = dot_name or bracket_name
            if name not in input_names:
                raise ValueError(f"UDT template references undeclared input {name!r}; no job submitted")
    for output in exact["outputs"]:
        source = output.get("format_source")
        if source is not None and (not isinstance(source, str) or source not in input_names):
            raise ValueError(f"Output {output['name']!r} format_source references undeclared input {source!r}")
        if "from_work_dir" in output and (not isinstance(output["from_work_dir"], str) or not output["from_work_dir"].strip()):
            raise ValueError(f"Output {output['name']!r} from_work_dir must be a nonempty filename")
    for requirement in exact.get("requirements") or []:
        if not isinstance(requirement, Mapping):
            raise ValueError("UDT requirements must contain JSON objects")
        if requirement.get("type") == "resource":
            fields = ("ram_min", "ram_max")
        elif requirement.get("class") == "ResourceRequirement":
            fields = ("ramMin", "ramMax")
        else:
            continue
        for field in fields:
            value = requirement.get(field)
            if value is None:
                continue
            try:
                amount = Decimal(str(value))
            except InvalidOperation:
                raise ValueError(f"{field} must be a numeric MiB value") from None
            if not amount.is_finite() or amount <= 0:
                raise ValueError(f"{field} must be a positive finite MiB value")
            # Benchmark safeguard, not a universal Galaxy RAM minimum.
            if amount < 128:
                raise ValueError(
                    f"{field}={value} requests less than 128 MiB; possible GiB/MiB mismatch. "
                    "Galaxy uses MiB (8 GiB = 8192), not GiB. "
                    "Specify the intended MiB request or omit the resource block for server defaults. "
                    "No job was submitted and no value was automatically converted."
                )
    return exact


def _resolve_quay_container_digest(
    container: str,
    *,
    request_get: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Resolve a public Quay tag to registry and Linux/AMD64 manifest digests."""

    reference = str(container).strip()
    record: dict[str, Any] = {"container": reference, "registry": "quay.io"}
    if reference.startswith("docker://") or "@sha256:" in reference:
        return {**record, "status": "invalid_reference"}
    match = re.fullmatch(r"quay\.io/([^:]+):([^/:]+)", reference)
    if match is None:
        return {**record, "status": "unsupported_or_untagged_reference"}
    repository, tag = match.groups()
    record.update({"repository": repository, "tag": tag})

    if request_get is None:
        import requests

        request_get = requests.get

    accept = ", ".join(
        (
            "application/vnd.oci.image.index.v1+json",
            "application/vnd.docker.distribution.manifest.list.v2+json",
            "application/vnd.oci.image.manifest.v1+json",
            "application/vnd.docker.distribution.manifest.v2+json",
        )
    )
    manifest_url = f"https://quay.io/v2/{repository}/manifests/{tag}"
    headers = {"Accept": accept}
    response = request_get(manifest_url, headers=headers, timeout=30)
    if response.status_code == 401:
        challenge = str(response.headers.get("WWW-Authenticate") or "")
        if not challenge.lower().startswith("bearer "):
            return {**record, "status": "registry_auth_unavailable"}
        params = dict(re.findall(r'(\w+)="([^"]*)"', challenge))
        realm = params.pop("realm", "")
        if not realm:
            return {**record, "status": "registry_auth_unavailable"}
        params.setdefault("scope", f"repository:{repository}:pull")
        token_response = request_get(realm, params=params, timeout=30)
        token_response.raise_for_status()
        token_payload = token_response.json()
        token = token_payload.get("token") or token_payload.get("access_token")
        if not token:
            return {**record, "status": "registry_auth_unavailable"}
        response = request_get(
            manifest_url,
            headers={"Accept": accept, "Authorization": f"Bearer {token}"},
            timeout=30,
        )
    response.raise_for_status()
    body = bytes(response.content)
    media_type = str(response.headers.get("Content-Type") or "").split(";", 1)[0]
    registry_digest = str(response.headers.get("Docker-Content-Digest") or "")
    if not registry_digest:
        registry_digest = f"sha256:{hashlib.sha256(body).hexdigest()}"
    payload = response.json()
    linux_amd64_digest = None
    for manifest in payload.get("manifests") or []:
        if not isinstance(manifest, Mapping):
            continue
        platform = manifest.get("platform")
        if not isinstance(platform, Mapping):
            continue
        if platform.get("os") == "linux" and platform.get("architecture") == "amd64":
            digest = manifest.get("digest")
            if isinstance(digest, str):
                linux_amd64_digest = digest
                break
    return {
        **record,
        "linux_amd64_digest": linux_amd64_digest,
        "media_type": media_type or payload.get("mediaType"),
        "registry_digest": registry_digest,
        "status": "ok",
    }


def run_udt_and_wait(
    *,
    history_id: str,
    representation: Mapping[str, Any],
    tool_inputs: Mapping[str, Any],
    create_user_tool: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    submit_user_tool: Callable[
        [str, str, Mapping[str, Any], str], Mapping[str, Any]
    ],
    fetch_job: Callable[[str], Mapping[str, Any]],
    workspace_root: Path,
    fetch_dataset: Callable[[str], Mapping[str, Any]] | None = None,
    fetch_collection: Callable[[str], Mapping[str, Any]] | None = None,
    resolve_container: Callable[[str], Mapping[str, Any]] | None = None,
    fetch_dataset_prefix: Callable[[str, int], bytes] | None = None,
    input_format: str = "auto",
    timeout_seconds: float | None = None,
    start_timeout_seconds: float | None = None,
    poll_interval_seconds: float = 10.0,
    evidence_directory: str = "run_trace/galaxy_udt_run",
    secrets: Sequence[str] = (),
) -> dict[str, Any]:
    """Create one exact agent-authored UDT, submit it, and block until terminal."""

    history_id = _validate_identifier(
        history_id,
        label="history ID",
        pattern=HISTORY_ID_PATTERN,
    )
    exact_representation = _validate_udt_representation(representation)
    if not isinstance(tool_inputs, Mapping):
        raise ValueError("tool_inputs must be a JSON object")
    exact_inputs = dict(tool_inputs)
    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    _write_json(
        evidence_path / "request.json",
        _redact(
            {
                "history_id": history_id,
                "input_format": input_format,
                "representation": exact_representation,
                "tool_inputs": exact_inputs,
            },
            secrets,
        ),
    )
    container_resolution: dict[str, Any] | None = None
    container = exact_representation.get("container")
    if isinstance(container, str) and container.strip():
        if resolve_container is None:
            container_resolution = {
                "container": container,
                "status": "not_requested",
            }
        else:
            try:
                container_resolution = dict(resolve_container(container))
            except Exception as exc:
                container_resolution = {
                    "container": container,
                    "error": str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:],
                    "status": "unavailable",
                }
        _write_json(
            evidence_path / "container_resolution.json",
            _redact(container_resolution, secrets),
        )

    try:
        created = _redact(dict(create_user_tool(exact_representation)), secrets)
    except Exception as exc:
        error = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
        _write_json(evidence_path / "creation_error.json", {"error": error})
        summary = {
            "evidence_directory": evidence_directory,
            "error": error,
            "status": "udt_creation_failed",
            "submitted": False,
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    _write_json(evidence_path / "creation_response.json", created)
    tool_uuid = created.get("uuid")
    if not isinstance(tool_uuid, str) or not tool_uuid.strip():
        summary = {
            "evidence_directory": evidence_directory,
            "status": "udt_creation_returned_no_uuid",
            "submitted": False,
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    result = run_tool_and_wait(
        history_id=history_id,
        tool_id=tool_uuid,
        tool_inputs=exact_inputs,
        build_tool=lambda *_args: {},
        submit_tool=lambda selected_history_id, _tool_id, selected_inputs, selected_format: submit_user_tool(
            selected_history_id,
            tool_uuid,
            selected_inputs,
            selected_format,
        ),
        fetch_job=fetch_job,
        fetch_dataset=fetch_dataset,
        fetch_collection=fetch_collection,
        fetch_dataset_prefix=fetch_dataset_prefix,
        workspace_root=workspace_root,
        input_format=input_format,
        validate_before_submit=False,
        timeout_seconds=timeout_seconds,
        start_timeout_seconds=start_timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
        evidence_directory=f"{evidence_directory}/execution",
        secrets=secrets,
    )
    summary = dict(result)
    summary["container_resolution"] = container_resolution
    summary["evidence_directory"] = evidence_directory
    summary["tool_uuid"] = tool_uuid
    summary.pop("tool_id", None)
    _write_json(evidence_path / "summary.json", summary)
    return summary


def _workspace_file(path: str, workspace_root: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    resolved_root = workspace_root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("path must resolve inside the agent workspace") from exc
    if not resolved.is_file():
        raise ValueError(f"workspace file does not exist: {path!r}")
    return resolved


def archive_inventory(
    *,
    path: str,
    workspace_root: Path,
    name_query: str | None = None,
    suffixes: Sequence[str] = (),
    sample_limit: int = 5,
    evidence_directory: str = "run_trace/archive_inventory",
) -> dict[str, Any]:
    """Inspect archive metadata without printing or extracting every member."""

    if not 1 <= sample_limit <= MAX_ARCHIVE_SAMPLE:
        raise ValueError(
            f"sample_limit must be between 1 and {MAX_ARCHIVE_SAMPLE}"
        )
    archive_path = _workspace_file(path, workspace_root)
    query = str(name_query or "").strip().casefold()
    normalized_suffixes = tuple(
        value if value.startswith(".") else f".{value}"
        for value in (str(item).strip().casefold() for item in suffixes)
        if value and value != "."
    )

    members: list[dict[str, Any]] = []
    if zipfile.is_zipfile(archive_path):
        archive_type = "zip"
        with zipfile.ZipFile(archive_path) as archive:
            for item in archive.infolist():
                members.append(
                    {
                        "compressed_size": item.compress_size,
                        "is_directory": item.is_dir(),
                        "name": item.filename,
                        "size": item.file_size,
                    }
                )
    elif tarfile.is_tarfile(archive_path):
        archive_type = "tar"
        with tarfile.open(archive_path, mode="r:*") as archive:
            for item in archive.getmembers():
                members.append(
                    {
                        "is_directory": item.isdir(),
                        "name": item.name,
                        "size": item.size,
                    }
                )
    else:
        raise ValueError("supported archive formats are ZIP and TAR variants")

    files = [item for item in members if not item["is_directory"]]
    selected = []
    for item in files:
        normalized_name = str(item["name"]).casefold()
        if query and query not in normalized_name:
            continue
        if normalized_suffixes and not normalized_name.endswith(normalized_suffixes):
            continue
        selected.append(item)

    suffix_counts = Counter(
        Path(str(item["name"])).suffix.casefold() or "<none>" for item in files
    )
    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    _write_json(
        evidence_path / "members.json",
        {
            "archive": str(archive_path.relative_to(workspace_root.resolve())),
            "archive_type": archive_type,
            "members": members,
        },
    )
    summary = {
        "archive": str(archive_path.relative_to(workspace_root.resolve())),
        "archive_type": archive_type,
        "directory_count": len(members) - len(files),
        "file_count": len(files),
        "filters": {
            "name_query": name_query,
            "suffixes": list(normalized_suffixes),
        },
        "sample": [item["name"] for item in selected[:sample_limit]],
        "selected_count": len(selected),
        "suffix_counts": dict(
            sorted(suffix_counts.items(), key=lambda item: (-item[1], item[0]))[:20]
        ),
    }
    _write_json(evidence_path / "summary.json", summary)
    return summary


def dataset_archive_inventory(
    *,
    dataset_id: str,
    download_dataset: Callable[[str, str], Any],
    workspace_root: Path,
    name_query: str | None = None,
    suffixes: Sequence[str] = (),
    sample_limit: int = 5,
    evidence_directory: str = "run_trace/archive_inventory",
) -> dict[str, Any]:
    """Download one owned Galaxy archive for bounded inventory inspection."""

    dataset_id = _validate_identifier(
        dataset_id,
        label="dataset ID",
        pattern=HISTORY_ID_PATTERN,
    )
    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    downloaded = evidence_path / "source.archive"
    try:
        download_dataset(dataset_id, str(downloaded))
        summary = archive_inventory(
            path=str(downloaded.relative_to(workspace_root.resolve())),
            workspace_root=workspace_root,
            name_query=name_query,
            suffixes=suffixes,
            sample_limit=sample_limit,
            evidence_directory=evidence_directory,
        )
    finally:
        downloaded.unlink(missing_ok=True)

    summary["archive"] = None
    summary["source_dataset_id"] = dataset_id
    _write_json(evidence_path / "summary.json", summary)
    members_path = evidence_path / "members.json"
    members = json.loads(members_path.read_text(encoding="utf-8"))
    members["archive"] = None
    members["source_dataset_id"] = dataset_id
    _write_json(members_path, members)
    return summary


def history_inventory(
    *,
    history_id: str,
    fetch_contents: Callable[[str], Sequence[Mapping[str, Any]]],
    workspace_root: Path,
    name_query: str | None = None,
    extensions: Sequence[str] = (),
    limit: int = 20,
    evidence_directory: str = "run_trace/galaxy_history_inventory",
    secrets: Sequence[str] = (),
) -> dict[str, Any]:
    """Return only matching history inputs while retaining the full response."""

    history_id = _validate_identifier(
        history_id,
        label="history ID",
        pattern=HISTORY_ID_PATTERN,
    )
    if not 1 <= limit <= MAX_HISTORY_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_HISTORY_RESULTS}")
    query = str(name_query or "").strip().casefold()
    normalized_extensions = {
        str(item).strip().casefold().lstrip(".")
        for item in extensions
        if str(item).strip()
    }
    contents = [dict(item) for item in fetch_contents(history_id)]
    redacted = _redact(contents, secrets)
    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    _write_json(evidence_path / "contents.json", redacted)

    state_counts: Counter[str] = Counter()
    matches: list[dict[str, Any]] = []
    for item in redacted:
        state_counts[str(item.get("state") or "unknown")] += 1
        name = str(item.get("name") or "")
        extension = str(item.get("extension") or "").casefold().lstrip(".")
        if query and query not in name.casefold():
            continue
        if normalized_extensions and extension not in normalized_extensions:
            continue
        matches.append(
            {
                "extension": item.get("extension"),
                "hid": item.get("hid"),
                "id": item.get("id"),
                "name": item.get("name"),
                "state": item.get("state"),
                "type": item.get("history_content_type") or item.get("type"),
            }
        )
    summary = {
        "filters": {
            "extensions": sorted(normalized_extensions),
            "name_query": name_query,
        },
        "history_id": history_id,
        "item_count": len(redacted),
        "matching_count": len(matches),
        "results": matches[:limit],
        "state_counts": dict(sorted(state_counts.items())),
        "truncated": len(matches) > limit,
    }
    _write_json(evidence_path / "summary.json", summary)
    return summary


def dataset_preview(
    *,
    history_id: str,
    dataset_id: str,
    fetch_dataset: Callable[[str], Mapping[str, Any]],
    workspace_root: Path,
    evidence_directory: str = "run_trace/galaxy_dataset_peek",
    secrets: Sequence[str] = (),
) -> dict[str, Any]:
    """Return Galaxy's bounded dataset peek and compact column metadata."""

    history_id = _validate_identifier(
        history_id,
        label="history ID",
        pattern=HISTORY_ID_PATTERN,
    )
    dataset_id = _validate_identifier(
        dataset_id,
        label="dataset ID",
        pattern=DATASET_ID_PATTERN,
    )
    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    _write_json(
        evidence_path / "request.json",
        {"dataset_id": dataset_id, "history_id": history_id},
    )

    dataset = _redact(dict(fetch_dataset(dataset_id)), secrets)
    _write_json(evidence_path / "dataset_response.json", dataset)
    observed_history_id = dataset.get("history_id")
    state = str(dataset.get("state") or "unknown")
    raw_peek = dataset.get("peek")
    peek = str(raw_peek) if raw_peek not in (None, "") else None
    peek_truncated = bool(peek and len(peek) > MAX_DATASET_PEEK_CHARS)
    if peek_truncated and peek is not None:
        peek = peek[:MAX_DATASET_PEEK_CHARS]

    column_metadata = {
        key.removeprefix("metadata_"): dataset[key]
        for key in (
            "metadata_column_names",
            "metadata_column_types",
            "metadata_columns",
            "metadata_comment_lines",
            "metadata_data_lines",
            "metadata_delimiter",
        )
        if dataset.get(key) not in (None, "", [], {})
    }
    if observed_history_id is None:
        status = "history_unverified"
    elif observed_history_id != history_id:
        status = "history_mismatch"
    elif state != "ok":
        status = "dataset_not_ready"
    else:
        status = "ok"
    summary = {
        "column_metadata": column_metadata,
        "dataset_id": dataset_id,
        "evidence_directory": evidence_directory,
        "extension": dataset.get("extension") or dataset.get("file_ext"),
        "file_size": dataset.get("file_size"),
        "hid": dataset.get("hid"),
        "history_id": history_id,
        "name": dataset.get("name"),
        "observed_history_id": observed_history_id,
        "peek": peek,
        "peek_sha256": (
            hashlib.sha256(peek.encode("utf-8")).hexdigest()
            if peek is not None
            else None
        ),
        "peek_truncated": peek_truncated,
        "state": state,
        "status": status,
    }
    _write_json(evidence_path / "summary.json", summary)
    return summary


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _galaxy_instance():
    from bioblend.galaxy import GalaxyInstance

    api_key = _read_api_key()
    galaxy_url = os.environ.get("GALAXY_URL", "https://usegalaxy.org").rstrip("/")
    return GalaxyInstance(galaxy_url, key=api_key), api_key


def _dataset_prefix_fetcher(api_key: str) -> Callable[[str, int], bytes]:
    import requests

    galaxy_url = os.environ.get("GALAXY_URL", "https://usegalaxy.org").rstrip("/")

    def fetch(dataset_id: str, byte_limit: int) -> bytes:
        dataset_id_checked = _validate_identifier(
            dataset_id,
            label="dataset ID",
            pattern=DATASET_ID_PATTERN,
        )
        if byte_limit < 1:
            raise ValueError("byte_limit must be positive")
        response = requests.get(
            f"{galaxy_url}/api/datasets/{dataset_id_checked}/display",
            params={"raw": "true"},
            headers={"x-api-key": api_key},
            stream=True,
            timeout=60,
        )
        response.raise_for_status()
        payload = bytearray()
        try:
            for chunk in response.iter_content(chunk_size=min(64 * 1024, byte_limit)):
                if not chunk:
                    continue
                payload.extend(chunk[: byte_limit - len(payload)])
                if len(payload) >= byte_limit:
                    break
        finally:
            response.close()
        return bytes(payload)

    return fetch


def _staging_upload_options(
    source: Path,
    requested_file_type: str,
) -> tuple[str, dict[str, bool]]:
    """Choose lossless Galaxy upload options for one workspace file."""

    lower_name = source.name.lower()
    upload_file_type = requested_file_type
    if requested_file_type == "auto":
        for suffix, inferred_type in sorted(
            COMPRESSED_TEXT_TYPES_BY_SUFFIX.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if lower_name.endswith(suffix):
                upload_file_type = inferred_type
                break

    compressed = lower_name.endswith((".gz", ".bz2", ".xz"))
    normalized_upload_type = upload_file_type.lower()
    supports_compression = (
        normalized_upload_type in {"auto", "data"}
        or normalized_upload_type.endswith(".gz")
        or "bgzip" in normalized_upload_type
        or "gzip" in normalized_upload_type
    )
    upload_flags: dict[str, bool] = {}
    if compressed:
        upload_flags["to_posix_lines"] = False
        if not supports_compression:
            upload_flags["auto_decompress"] = True
    return upload_file_type, upload_flags


def _wait_for_staged_datasets(
    *,
    history_id: str,
    dataset_refs: Sequence[Mapping[str, Any]],
    fetch_dataset: Callable[[str], Mapping[str, Any]],
    workspace_root: Path,
    evidence_directory: str,
    poll_interval_seconds: float = 2.0,
    secrets: Sequence[str] = (),
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Wait until staged datasets finish datatype and metadata processing."""

    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    events_path = evidence_path / "state_changes.jsonl"
    if events_path.exists():
        events_path.unlink()

    dataset_ids: list[str] = []
    for ref in dataset_refs:
        raw_id = ref.get("id")
        if not isinstance(raw_id, str):
            continue
        dataset_id = _validate_identifier(
            raw_id,
            label="dataset ID",
            pattern=DATASET_ID_PATTERN,
        )
        if dataset_id not in dataset_ids:
            dataset_ids.append(dataset_id)
    if not dataset_ids:
        summary = {
            "datasets": [],
            "elapsed_seconds": 0.0,
            "failure_summary": "Upload response contained no output dataset ID.",
            "status": "missing_output_dataset",
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    started = monotonic()
    pending = set(dataset_ids)
    last_states: dict[str, str] = {}
    final_details: dict[str, dict[str, Any]] = {}
    failure_status: str | None = None
    failure_summary: str | None = None
    while pending and failure_status is None:
        for dataset_id in list(pending):
            try:
                detail = dict(fetch_dataset(dataset_id))
            except Exception as exc:
                failure_status = "dataset_lookup_failed"
                failure_summary = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
                break
            state = str(detail.get("state") or "unknown").lower()
            observed_history_id = detail.get("history_id")
            compact = {
                "data_type": detail.get("data_type"),
                "file_ext": detail.get("file_ext") or detail.get("extension"),
                "history_id": observed_history_id,
                "id": dataset_id,
                "name": detail.get("name"),
                "state": state,
            }
            final_details[dataset_id] = _redact(compact, secrets)
            if last_states.get(dataset_id) != state:
                _append_jsonl(
                    events_path,
                    _redact({"dataset_id": dataset_id, "state": state}, secrets),
                )
                last_states[dataset_id] = state
            if observed_history_id not in (None, history_id):
                failure_status = "dataset_history_mismatch"
                failure_summary = (
                    f"Dataset {dataset_id} belongs to history "
                    f"{observed_history_id}, not {history_id}."
                )
                break
            if state == "ok":
                pending.remove(dataset_id)
            elif state in STAGED_DATASET_FAILURE_STATES:
                failure_status = "dataset_error"
                failure_summary = (
                    f"Dataset {dataset_id} entered terminal state {state}."
                )
                break
        if pending and failure_status is None:
            sleep(poll_interval_seconds)

    summary = {
        "datasets": [final_details[item] for item in dataset_ids if item in final_details],
        "elapsed_seconds": round(monotonic() - started, 3),
        "failure_summary": failure_summary,
        "status": failure_status or "ok",
    }
    _write_json(evidence_path / "final_datasets.json", summary["datasets"])
    _write_json(evidence_path / "summary.json", summary)
    return summary


def _wait_for_output_collections(
    *,
    history_id: str,
    collection_refs: Sequence[Mapping[str, Any]],
    fetch_collection: Callable[[str], Mapping[str, Any]],
    workspace_root: Path,
    evidence_directory: str,
    poll_interval_seconds: float = 2.0,
    secrets: Sequence[str] = (),
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Resolve output collections and return every contained dataset ref."""

    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    events_path = evidence_path / "state_changes.jsonl"
    if events_path.exists():
        events_path.unlink()

    pending: list[str] = []
    for ref in collection_refs:
        raw_id = ref.get("id")
        if isinstance(raw_id, str):
            collection_id = _validate_identifier(
                raw_id,
                label="dataset collection ID",
                pattern=DATASET_ID_PATTERN,
            )
            if collection_id not in pending:
                pending.append(collection_id)
    if not pending:
        summary = {
            "collections": [],
            "dataset_refs": [],
            "elapsed_seconds": 0.0,
            "failure_summary": "Submission contained no output collection ID.",
            "status": "missing_output_collection",
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    started = monotonic()
    seen: set[str] = set()
    dataset_refs: list[dict[str, str]] = []
    collection_records: list[dict[str, Any]] = []
    failure_status: str | None = None
    failure_summary: str | None = None

    def add_dataset_ref(value: Mapping[str, Any]) -> None:
        raw_id = value.get("id")
        if not isinstance(raw_id, str):
            return
        ref = {
            "id": _validate_identifier(
                raw_id,
                label="dataset ID",
                pattern=DATASET_ID_PATTERN,
            ),
            "src": str(value.get("src") or "hda"),
        }
        if ref not in dataset_refs:
            dataset_refs.append(ref)

    def visit_elements(elements: Any) -> None:
        if not isinstance(elements, list):
            return
        for element in elements:
            if not isinstance(element, Mapping):
                continue
            element_type = str(element.get("element_type") or "").lower()
            obj = element.get("object")
            if not isinstance(obj, Mapping):
                obj = element
            if element_type in {"hda", "ldda", "dataset"} or str(
                obj.get("src") or ""
            ).lower() in {"hda", "ldda"}:
                add_dataset_ref(obj)
                continue
            if element_type in {"dataset_collection", "hdca", "collection"} or isinstance(
                obj.get("elements"), list
            ):
                nested_id = obj.get("id")
                if isinstance(obj.get("elements"), list):
                    visit_elements(obj["elements"])
                elif isinstance(nested_id, str) and nested_id not in seen and nested_id not in pending:
                    pending.append(nested_id)

    while pending and failure_status is None:
        collection_id = pending.pop(0)
        if collection_id in seen:
            continue
        try:
            detail = dict(fetch_collection(collection_id))
        except Exception as exc:
            failure_status = "collection_lookup_failed"
            failure_summary = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
            break
        observed_history_id = detail.get("history_id")
        state = str(
            detail.get("populated_state") or detail.get("state") or "unknown"
        ).lower()
        if observed_history_id not in (None, history_id):
            failure_status = "collection_history_mismatch"
            failure_summary = (
                f"Dataset collection {collection_id} belongs to history "
                f"{observed_history_id}, not {history_id}."
            )
            break
        if state in STAGED_DATASET_FAILURE_STATES:
            failure_status = "collection_error"
            failure_summary = (
                f"Dataset collection {collection_id} entered terminal state {state}."
            )
            break
        if state in {"new", "running", "queued", "setting_metadata"} or "elements" not in detail:
            pending.append(collection_id)
            sleep(poll_interval_seconds)
            continue
        seen.add(collection_id)
        record = {
            "history_id": observed_history_id,
            "id": collection_id,
            "name": detail.get("name"),
            "state": state,
        }
        collection_records.append(_redact(record, secrets))
        _append_jsonl(events_path, _redact(record, secrets))
        visit_elements(detail.get("elements"))

    summary = {
        "collections": collection_records,
        "dataset_refs": dataset_refs,
        "elapsed_seconds": round(monotonic() - started, 3),
        "failure_summary": failure_summary,
        "status": failure_status or "ok",
    }
    _write_json(evidence_path / "collections.json", collection_records)
    _write_json(evidence_path / "summary.json", summary)
    return summary


def stage_file_and_wait(
    *,
    history_id: str,
    path: str,
    name: str | None,
    file_type: str,
    upload_file: Callable[..., Mapping[str, Any]],
    fetch_job: Callable[[str], Mapping[str, Any]],
    fetch_dataset: Callable[[str], Mapping[str, Any]],
    workspace_root: Path,
    evidence_directory: str,
    secrets: Sequence[str] = (),
) -> dict[str, Any]:
    """Stage one workspace file and verify its final Galaxy dataset state."""

    history_id = _validate_identifier(
        history_id,
        label="history ID",
        pattern=HISTORY_ID_PATTERN,
    )
    source = _workspace_file(path, workspace_root)
    staged_name = str(name).strip() if name is not None else source.name
    if not staged_name or len(staged_name) > 255 or "/" in staged_name or "\\" in staged_name:
        raise ValueError("name must be a basename containing 1-255 characters")
    normalized_type = str(file_type).strip()
    if not re.fullmatch(r"[A-Za-z0-9_.+\-]{1,64}", normalized_type):
        raise ValueError("file_type contains unsupported characters")
    upload_file_type, upload_flags = _staging_upload_options(
        source,
        normalized_type,
    )

    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    source_record = {
        "file_type": normalized_type,
        "history_id": history_id,
        "name": staged_name,
        "path": str(source.relative_to(workspace_root.resolve())),
        "sha256": _sha256_file(source),
        "size_bytes": source.stat().st_size,
        "upload_auto_decompress": upload_flags.get("auto_decompress", False),
        "upload_file_type": upload_file_type,
        "upload_to_posix_lines": upload_flags.get("to_posix_lines"),
    }
    _write_json(evidence_path / "request.json", source_record)
    try:
        submission = dict(
            upload_file(
                str(source),
                history_id,
                file_name=staged_name,
                file_type=upload_file_type,
                **upload_flags,
            )
        )
    except Exception as exc:
        error = str(_redact(str(exc), secrets))[-MAX_ERROR_CHARS:]
        summary = {
            **source_record,
            "error": error,
            "evidence_directory": evidence_directory,
            "status": "upload_failed",
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    redacted_submission = _redact(submission, secrets)
    _write_json(evidence_path / "submission_response.json", redacted_submission)
    job_ids = _job_ids_from_submission(submission)
    output_refs = _extract_dataset_refs(submission.get("outputs") or [])
    if job_ids:
        wait_result = wait_for_jobs(
            job_ids,
            fetch_job=fetch_job,
            workspace_root=workspace_root,
            evidence_directory=f"{evidence_directory}/wait",
            timeout_seconds=None,
            start_timeout_seconds=None,
            poll_interval_seconds=10.0,
            secrets=secrets,
        )
        status = wait_result["status"]
        elapsed_seconds = wait_result["elapsed_seconds"]
        failure_summary = wait_result["failure_summary"]
    else:
        status = "submitted_no_jobs"
        elapsed_seconds = 0.0
        failure_summary = None
    dataset_result: dict[str, Any] | None = None
    if status in {"ok", "submitted_no_jobs"}:
        dataset_result = _wait_for_staged_datasets(
            history_id=history_id,
            dataset_refs=output_refs,
            fetch_dataset=fetch_dataset,
            workspace_root=workspace_root,
            evidence_directory=f"{evidence_directory}/datasets",
            secrets=secrets,
        )
        status = dataset_result["status"]
        elapsed_seconds += dataset_result["elapsed_seconds"]
        failure_summary = dataset_result["failure_summary"]
    summary = {
        **source_record,
        "elapsed_seconds": elapsed_seconds,
        "evidence_directory": evidence_directory,
        "failure_summary": failure_summary,
        "output_datasets": (
            dataset_result.get("datasets", []) if dataset_result is not None else []
        ),
        "output_dataset_refs": output_refs,
        "status": status,
    }
    _write_json(evidence_path / "summary.json", summary)
    return summary


def _bind_udt_workspace_inputs(
    *,
    history_id: str,
    representation: Mapping[str, Any],
    tool_inputs: Mapping[str, Any],
    workspace_inputs: Mapping[str, Mapping[str, Any]],
    upload_file: Callable[..., Mapping[str, Any]],
    fetch_job: Callable[[str], Mapping[str, Any]],
    fetch_dataset: Callable[[str], Mapping[str, Any]],
    workspace_root: Path,
    evidence_directory: str,
    secrets: Sequence[str] = (),
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
    """Stage and bind optional workspace files before one UDT submission."""

    if len(workspace_inputs) > MAX_UDT_WORKSPACE_INPUTS:
        raise ValueError(
            f"workspace_inputs may contain at most {MAX_UDT_WORKSPACE_INPUTS} entries"
        )
    representation_inputs = {
        str(item.get("name")): item
        for item in representation.get("inputs", [])
        if isinstance(item, Mapping) and item.get("name")
    }
    prepared: list[tuple[str, str, str | None, str]] = []
    for input_name, raw_spec in workspace_inputs.items():
        if input_name not in representation_inputs:
            raise ValueError(
                f"workspace input {input_name!r} is not a top-level UDT input"
            )
        if representation_inputs[input_name].get("type") != "data":
            raise ValueError(
                f"workspace input {input_name!r} must bind a data input"
            )
        if input_name in tool_inputs:
            raise ValueError(
                f"workspace input {input_name!r} is already present in tool_inputs"
            )
        if not isinstance(raw_spec, Mapping):
            raise ValueError(f"workspace input {input_name!r} must be a JSON object")
        unknown_keys = sorted(set(raw_spec) - {"file_type", "name", "path"})
        if unknown_keys:
            raise ValueError(
                f"workspace input {input_name!r} has unsupported keys: {unknown_keys}"
            )
        path = raw_spec.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"workspace input {input_name!r} requires path")
        _workspace_file(path, workspace_root)
        name = raw_spec.get("name")
        if name is not None and not isinstance(name, str):
            raise ValueError(f"workspace input {input_name!r} name must be a string")
        file_type = raw_spec.get("file_type", "auto")
        if not isinstance(file_type, str):
            raise ValueError(
                f"workspace input {input_name!r} file_type must be a string"
            )
        prepared.append((input_name, path, name, file_type))

    resolved_inputs = dict(tool_inputs)
    records: list[dict[str, Any]] = []
    for index, (input_name, path, name, file_type) in enumerate(prepared, start=1):
        result = stage_file_and_wait(
            history_id=history_id,
            path=path,
            name=name,
            file_type=file_type,
            upload_file=upload_file,
            fetch_job=fetch_job,
            fetch_dataset=fetch_dataset,
            workspace_root=workspace_root,
            evidence_directory=f"{evidence_directory}/staging/{index:03d}",
            secrets=secrets,
        )
        record = {"input_name": input_name, **result}
        records.append(record)
        refs = result.get("output_dataset_refs") or []
        if result.get("status") != "ok" or len(refs) != 1:
            return (
                resolved_inputs,
                records,
                {
                    "failed_input": input_name,
                    "staging_status": result.get("status"),
                    "status": "workspace_staging_failed",
                },
            )
        dataset_id = refs[0].get("id")
        if not isinstance(dataset_id, str):
            return (
                resolved_inputs,
                records,
                {
                    "failed_input": input_name,
                    "staging_status": "missing_dataset_id",
                    "status": "workspace_staging_failed",
                },
            )
        resolved_inputs[input_name] = {"id": dataset_id, "src": "hda"}
    return resolved_inputs, records, None


def stage_workspace_file(
    history_id: str,
    path: str,
    name: str | None = None,
    file_type: str = "auto",
) -> dict[str, Any]:
    """Stage one workspace file and block until its dataset is usable."""

    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))
    galaxy, api_key = _galaxy_instance()
    evidence_directory = _next_evidence_directory(
        workspace_root,
        "run_trace/galaxy_file_stage",
    )
    return stage_file_and_wait(
        history_id=history_id,
        path=path,
        name=name,
        file_type=file_type,
        upload_file=galaxy.tools.upload_file,
        fetch_job=lambda job_id: galaxy.jobs.show_job(job_id, full_details=True),
        fetch_dataset=lambda dataset_id: galaxy.datasets.show_dataset(
            dataset_id,
            hda_ldda="hda",
        ),
        workspace_root=workspace_root,
        evidence_directory=evidence_directory,
        secrets=(api_key,),
    )


def search_galaxy_tools(
    query: str,
) -> dict[str, Any]:
    """Search by package, tool family, operation class, or target metric.

    Use this instead of BioBlend ``get_tools()``.
    """

    import requests

    galaxy, api_key = _galaxy_instance()
    galaxy_url = os.environ.get("GALAXY_URL", "https://usegalaxy.org").rstrip("/")
    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))

    def fetch_capability_ids(probe: str) -> Sequence[str]:
        response = requests.get(
            f"{galaxy_url}/api/tools",
            params={"q": probe},
            headers={"x-api-key": api_key},
            timeout=60,
        )
        response.raise_for_status()
        value = response.json()
        if not isinstance(value, list):
            raise ValueError("Galaxy capability search did not return a list")
        return [item for item in value if isinstance(item, str)]

    return search_tool_list(
        query=query,
        limit=MAX_SEARCH_RESULTS,
        evidence_directory=_next_evidence_directory(
            workspace_root,
            "run_trace/galaxy_tool_search",
        ),
        fetch_capability_ids=fetch_capability_ids,
        fetch_tools=galaxy.tools.get_tools,
        workspace_root=workspace_root,
        secrets=(api_key,),
    )


def inspect_galaxy_history(
    history_id: str,
    name_query: str | None = None,
    extensions: list[str] | None = None,
) -> dict[str, Any]:
    """Return a compact dataset lookup without printing full history contents."""

    galaxy, api_key = _galaxy_instance()
    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))
    return history_inventory(
        history_id=history_id,
        name_query=name_query,
        extensions=extensions or [],
        limit=20,
        fetch_contents=lambda selected_history_id: galaxy.histories.show_history(
            selected_history_id,
            contents=True,
        ),
        evidence_directory=_next_evidence_directory(
            workspace_root,
            "run_trace/galaxy_history_inventory",
        ),
        workspace_root=workspace_root,
        secrets=(api_key,),
    )


def peek_galaxy_dataset(
    history_id: str,
    dataset_id: str,
) -> dict[str, Any]:
    """Return a bounded Galaxy preview and column metadata for one history dataset."""

    galaxy, api_key = _galaxy_instance()
    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))
    return dataset_preview(
        history_id=history_id,
        dataset_id=dataset_id,
        fetch_dataset=lambda selected_id: galaxy.datasets.show_dataset(
            selected_id,
            hda_ldda="hda",
        ),
        evidence_directory=_next_evidence_directory(
            workspace_root,
            "run_trace/galaxy_dataset_peek",
        ),
        workspace_root=workspace_root,
        secrets=(api_key,),
    )


def inspect_archive_inventory(
    path: str | None = None,
    dataset_id: str | None = None,
    history_id: str | None = None,
    name_query: str | None = None,
    suffixes: list[str] | None = None,
) -> dict[str, Any]:
    """Inspect one archive compactly by workspace path or Galaxy dataset ID.

    For a Galaxy dataset, provide both ``dataset_id`` and ``history_id``.
    Provide exactly one source.
    """

    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))
    if (path is None) == (dataset_id is None):
        raise ValueError("provide exactly one of path or dataset_id")
    evidence_directory = _next_evidence_directory(
        workspace_root,
        "run_trace/archive_inventory",
    )
    if dataset_id is not None:
        if history_id is None:
            raise ValueError("history_id is required with dataset_id")
        dataset_id = _validate_identifier(
            dataset_id,
            label="dataset ID",
            pattern=DATASET_ID_PATTERN,
        )
        history_id = _validate_identifier(
            history_id,
            label="history ID",
            pattern=HISTORY_ID_PATTERN,
        )
        galaxy, api_key = _galaxy_instance()
        dataset = _redact(
            dict(galaxy.datasets.show_dataset(dataset_id, hda_ldda="hda")),
            (api_key,),
        )
        if dataset.get("history_id") != history_id:
            raise ValueError("archive dataset does not belong to the selected history")
        if dataset.get("state") != "ok":
            raise ValueError("archive dataset must be in ok state")
        result = dataset_archive_inventory(
            dataset_id=dataset_id,
            name_query=name_query,
            suffixes=suffixes or [],
            sample_limit=5,
            download_dataset=lambda selected_id, destination: galaxy.datasets.download_dataset(
                selected_id,
                file_path=destination,
                use_default_filename=False,
            ),
            evidence_directory=evidence_directory,
            workspace_root=workspace_root,
        )
        result["history_id"] = history_id
        evidence_path = _resolve_evidence_directory(
            workspace_root,
            evidence_directory,
        )
        _write_json(evidence_path / "dataset_response.json", dataset)
        _write_json(evidence_path / "summary.json", result)
        return result
    if history_id is not None:
        raise ValueError("history_id is only valid with dataset_id")
    assert path is not None
    return archive_inventory(
        path=path,
        name_query=name_query,
        suffixes=suffixes or [],
        sample_limit=5,
        evidence_directory=evidence_directory,
        workspace_root=workspace_root,
    )


def inspect_galaxy_tool(
    tool_id: str,
    history_id: str | None = None,
    field_filter: list[str] | None = None,
    selector_values: dict[str, Any] | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    """Inspect one selected tool with a compact live schema.

    Set ``field_filter`` to the requested metric or operation terms on the
    first call. Use ``selector_values`` to narrow conditional branches.
    Unchanged repeat replies are abbreviated; set ``refresh=true`` to reread.
    """

    galaxy, api_key = _galaxy_instance()
    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))
    return inspect_tool_schema(
        tool_id=tool_id,
        history_id=history_id,
        field_filter=field_filter or [],
        selector_values=selector_values or {},
        refresh=refresh,
        evidence_directory=_next_evidence_directory(
            workspace_root,
            "run_trace/galaxy_tool_schema",
        ),
        field_limit=80,
        build_tool=lambda selected_tool_id, selected_history_id: galaxy.tools.build(
            selected_tool_id,
            history_id=selected_history_id,
        ),
        show_tool=lambda selected_tool_id: galaxy.tools.show_tool(
            selected_tool_id,
            io_details=True,
            link_details=True,
        ),
        workspace_root=workspace_root,
        secrets=(api_key,),
    )


def run_galaxy_tool_and_wait(
    history_id: str,
    tool_id: str,
    tool_inputs: dict[str, Any],
    input_format: Literal["auto", "21.01", "legacy"] = "auto",
    validate_before_submit: bool = True,
) -> dict[str, Any]:
    """Submit and block; use this instead of BioBlend run_tool() plus polling."""

    galaxy, api_key = _galaxy_instance()
    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))
    return run_tool_and_wait(
        history_id=history_id,
        tool_id=tool_id,
        tool_inputs=tool_inputs,
        input_format=input_format,
        validate_before_submit=validate_before_submit,
        timeout_seconds=None,
        start_timeout_seconds=None,
        poll_interval_seconds=10.0,
        evidence_directory=_next_evidence_directory(
            workspace_root,
            "run_trace/galaxy_tool_run",
        ),
        build_tool=lambda selected_tool_id, selected_inputs, selected_history_id: galaxy.tools.build(
            selected_tool_id,
            inputs=selected_inputs,
            history_id=selected_history_id,
        ),
        submit_tool=lambda selected_history_id, selected_tool_id, selected_inputs, selected_format: galaxy.tools.run_tool(
            selected_history_id,
            selected_tool_id,
            selected_inputs,
            input_format=selected_format,
        ),
        fetch_job=lambda job_id: galaxy.jobs.show_job(job_id, full_details=True),
        fetch_dataset=lambda dataset_id: galaxy.datasets.show_dataset(
            dataset_id,
            hda_ldda="hda",
        ),
        fetch_collection=lambda collection_id: galaxy.dataset_collections.show_dataset_collection(
            collection_id
        ),
        fetch_dataset_prefix=_dataset_prefix_fetcher(api_key),
        workspace_root=workspace_root,
        secrets=(api_key,),
    )


def run_galaxy_udt_and_wait(
    history_id: str,
    representation: dict[str, Any],
    tool_inputs: dict[str, Any],
    input_format: Literal["auto", "21.01", "legacy"] = "auto",
    workspace_inputs: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Optionally stage workspace inputs, then create, submit, and block once."""

    galaxy, api_key = _galaxy_instance()
    if not hasattr(galaxy, "unprivileged_tools"):
        return {
            "evidence_directory": None,
            "status": "bioblend_udt_interface_unavailable",
            "submitted": False,
        }
    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))
    evidence_directory = _next_evidence_directory(
        workspace_root,
        "run_trace/galaxy_udt_run",
    )
    exact_representation = _validate_udt_representation(representation)
    if not isinstance(tool_inputs, Mapping):
        raise ValueError("tool_inputs must be a JSON object")
    workspace_specs = workspace_inputs or {}
    if not isinstance(workspace_specs, Mapping):
        raise ValueError("workspace_inputs must be a JSON object")
    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    _write_json(
        evidence_path / "workspace_inputs_request.json",
        _redact(dict(workspace_specs), (api_key,)),
    )
    resolved_inputs, staging_records, staging_failure = _bind_udt_workspace_inputs(
        history_id=history_id,
        representation=exact_representation,
        tool_inputs=tool_inputs,
        workspace_inputs=workspace_specs,
        upload_file=galaxy.tools.upload_file,
        fetch_job=lambda job_id: galaxy.jobs.show_job(job_id, full_details=True),
        fetch_dataset=lambda dataset_id: galaxy.datasets.show_dataset(
            dataset_id,
            hda_ldda="hda",
        ),
        workspace_root=workspace_root,
        evidence_directory=evidence_directory,
        secrets=(api_key,),
    )
    if staging_failure is not None:
        summary = {
            **staging_failure,
            "evidence_directory": evidence_directory,
            "submitted": False,
            "workspace_staging": staging_records,
        }
        _write_json(evidence_path / "summary.json", summary)
        return summary

    result = run_udt_and_wait(
        history_id=history_id,
        representation=exact_representation,
        tool_inputs=resolved_inputs,
        input_format=input_format,
        timeout_seconds=None,
        start_timeout_seconds=None,
        poll_interval_seconds=10.0,
        evidence_directory=evidence_directory,
        create_user_tool=lambda exact_representation: galaxy.unprivileged_tools.create_user_tool(
            exact_representation
        ),
        submit_user_tool=lambda selected_history_id, tool_uuid, selected_inputs, selected_format: galaxy.tools.run_tool(
            history_id=selected_history_id,
            tool_uuid=tool_uuid,
            tool_inputs=selected_inputs,
            input_format=selected_format,
        ),
        fetch_job=lambda job_id: galaxy.jobs.show_job(job_id, full_details=True),
        fetch_dataset=lambda dataset_id: galaxy.datasets.show_dataset(
            dataset_id,
            hda_ldda="hda",
        ),
        fetch_collection=lambda collection_id: galaxy.dataset_collections.show_dataset_collection(
            collection_id
        ),
        resolve_container=_resolve_quay_container_digest,
        fetch_dataset_prefix=_dataset_prefix_fetcher(api_key),
        workspace_root=workspace_root,
        secrets=(api_key,),
    )
    summary = dict(result)
    summary["workspace_staging"] = staging_records
    _write_json(evidence_path / "summary.json", summary)
    return summary


def serve() -> None:
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("galaxy-execute")
    server.tool(name="stage_workspace_file")(stage_workspace_file)
    server.tool(name="search_galaxy_tools")(search_galaxy_tools)
    server.tool(name="inspect_galaxy_history")(inspect_galaxy_history)
    server.tool(name="peek_galaxy_dataset")(peek_galaxy_dataset)
    server.tool(name="inspect_archive_inventory")(inspect_archive_inventory)
    server.tool(name="inspect_galaxy_tool")(inspect_galaxy_tool)
    server.tool(name="run_galaxy_tool_and_wait")(run_galaxy_tool_and_wait)
    server.tool(name="run_galaxy_udt_and_wait")(run_galaxy_udt_and_wait)
    server.run(transport="stdio")


if __name__ == "__main__":
    serve()
