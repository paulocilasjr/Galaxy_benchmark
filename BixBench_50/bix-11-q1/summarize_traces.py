"""Read-only summary of preserved original run traces and evaluator outputs."""
import json
import pathlib
import re
import gzip
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent / "source_snapshots/huggingface_traces/files"


def load(path):
    return json.loads(path.read_text()) if path.exists() else {}


def locate(folder, name):
    matches = list(folder.rglob(name))
    return matches[0] if matches else folder / name


def main():
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir() or not (folder / "evaluation.json").exists():
            continue
        evaluation = load(folder / "evaluation.json")
        usage = load(folder / "usage.json")
        invocation = load(locate(folder, "docker_invocation.json"))
        answer_files = list(folder.rglob("answer.txt"))
        answer = answer_files[0].read_text().strip() if answer_files else None
        event_path = locate(folder, "codex_events.jsonl")
        if not event_path.exists():
            event_path = locate(folder, "codex_events.jsonl.gz")
        events = []
        if event_path.exists():
            content = gzip.decompress(event_path.read_bytes()).decode(errors="replace") if event_path.suffix == ".gz" else event_path.read_text()
            for line in content.splitlines():
                if line.lstrip().startswith("{"):
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        completed = [x["item"] for x in events if x.get("type") == "item.completed" and x.get("item")]
        commands = [x for x in completed if x.get("type") == "command_execution"]
        mcp = [x for x in completed if x.get("type") == "mcp_tool_call"]
        bad = [x for x in commands if x.get("exit_code") not in (None, 0)]
        ids = Counter(re.findall(r"bbd44e69cb8906b[0-9a-f]{17}", content if event_path.exists() else ""))
        print(json.dumps({"label": folder.name, "answer": answer, "accuracy": evaluation.get("accuracy", {}).get("score"), "step_completion": evaluation.get("step_completion", {}).get("score"), "mode": evaluation.get("accuracy", {}).get("mode"), "model": invocation.get("model"), "reasoning": invocation.get("reasoning_effort"), "input_tokens": usage.get("totals", {}).get("input_tokens"), "output_tokens": usage.get("totals", {}).get("output_tokens"), "commands": len(commands), "nonzero_commands": len(bad), "mcp_calls": len(mcp), "mcp_tools": dict(Counter(x.get("tool") for x in mcp)), "history_ids": ids.most_common(3)}))


if __name__ == "__main__":
    main()
