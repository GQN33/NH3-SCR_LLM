from __future__ import annotations

import json
import os
import random
import re
import time
from pathlib import Path
from typing import Any

import requests


DEFAULT_API_URL = "https://api.openai.com/v1/responses"

REPO_ROOT = Path(__file__).resolve().parents[3]


def load_prompt_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_json_block(text: str) -> str:
    text = strip_code_fence(text)
    if text.startswith("{") or text.startswith("["):
        return text
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON block found in model response")
    return match.group(1).strip()


def parse_json_response(text: str) -> dict[str, Any]:
    payload = json.loads(extract_json_block(text))
    if not isinstance(payload, dict):
        raise ValueError("Model response JSON is not an object")
    return payload


def list_markdown_files(md_dir: Path) -> list[Path]:
    return sorted(md_dir.glob("*.md"))


def sample_markdown_files(md_dir: Path, sample_size: int, seed: int) -> list[Path]:
    files = list_markdown_files(md_dir)
    if len(files) < sample_size:
        raise RuntimeError(f"Only found {len(files)} markdown files in {md_dir}, fewer than requested {sample_size}")
    rng = random.Random(seed)
    return sorted(rng.sample(files, sample_size), key=lambda p: p.name.lower())


def prepare_prompt(prompt_text: str, article_text: str, catalyst_ids: list[str] | None = None, initial_graph: dict[str, Any] | None = None) -> str:
    prompt = prompt_text.replace("{ARTICLE_TEXT}", article_text)
    prompt = prompt.replace("{CATALYST_IDS_FROM_SYNTHESIS}", json.dumps(catalyst_ids or [], ensure_ascii=False))
    prompt = prompt.replace("{INITIAL_GRAPH_JSON}", json.dumps(initial_graph or {}, ensure_ascii=False, indent=2))
    return prompt


def call_openai(prompt_text: str, model: str, api_key: str, api_url: str = DEFAULT_API_URL, timeout_s: int = 300) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if api_url.endswith("/chat/completions"):
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0.0,
        }
    else:
        payload = {
            "model": model,
            "input": prompt_text,
        }
    response = requests.post(api_url, headers=headers, json=payload, timeout=timeout_s)
    response.raise_for_status()
    data = response.json()
    if api_url.endswith("/chat/completions"):
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No choices found in chat completion response")
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
            if parts:
                return "\n".join(parts).strip()
        raise ValueError("No text content found in chat completion response")
    if "output_text" in data and isinstance(data["output_text"], str):
        return data["output_text"]

    output = data.get("output", [])
    parts: list[str] = []
    for item in output:
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content.get("text", ""))
    if not parts:
        raise ValueError("No text content found in OpenAI response payload")
    return "\n".join(parts).strip()


def _ensure_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _ensure_list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def summarize_graph(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = _ensure_list_of_dicts(graph.get("nodes"))
    edges = _ensure_list_of_dicts(graph.get("edges"))
    node_type_counts: dict[str, int] = {}
    edge_type_counts: dict[str, int] = {}

    for node in nodes:
        node_type = str(node.get("type", "unknown"))
        node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
    for edge in edges:
        edge_type = str(edge.get("type", "unknown"))
        edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1

    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "node_type_counts": node_type_counts,
        "edge_type_counts": edge_type_counts,
        "has_paper": node_type_counts.get("paper", 0) > 0,
        "has_catalyst": node_type_counts.get("catalyst", 0) > 0,
        "has_poisoned_catalyst": node_type_counts.get("poisoned_catalyst", 0) > 0,
        "has_preparation": node_type_counts.get("preparation", 0) > 0,
        "has_testing": node_type_counts.get("testing", 0) > 0,
        "has_characterization": node_type_counts.get("characterization", 0) > 0,
    }


def merge_graphs(graphs: list[dict[str, Any]]) -> dict[str, Any]:
    node_map: dict[str, dict[str, Any]] = {}
    edge_map: dict[str, dict[str, Any]] = {}
    for graph in graphs:
        for node in _ensure_list_of_dicts(graph.get("nodes")):
            node_id = str(node.get("id", ""))
            if node_id:
                node_map[node_id] = node
        for edge in _ensure_list_of_dicts(graph.get("edges")):
            edge_id = str(edge.get("id", ""))
            if edge_id:
                edge_map[edge_id] = edge
    return {
        "nodes": list(node_map.values()),
        "edges": list(edge_map.values()),
    }


def apply_missing_check(base_graph: dict[str, Any], patch_graph: dict[str, Any]) -> dict[str, Any]:
    nodes = {str(node.get("id", "")): node for node in _ensure_list_of_dicts(base_graph.get("nodes")) if node.get("id")}
    edges = {str(edge.get("id", "")): edge for edge in _ensure_list_of_dicts(base_graph.get("edges")) if edge.get("id")}

    for node_id in _ensure_list_of_strings(patch_graph.get("node_ids_to_delete")):
        nodes.pop(node_id, None)
    for edge_id in _ensure_list_of_strings(patch_graph.get("edge_ids_to_delete")):
        edges.pop(edge_id, None)

    for node in _ensure_list_of_dicts(patch_graph.get("nodes_to_add")) + _ensure_list_of_dicts(patch_graph.get("nodes_to_update")):
        node_id = str(node.get("id", ""))
        if node_id:
            nodes[node_id] = node
    for edge in _ensure_list_of_dicts(patch_graph.get("edges_to_add")) + _ensure_list_of_dicts(patch_graph.get("edges_to_update")):
        edge_id = str(edge.get("id", ""))
        if edge_id:
            edges[edge_id] = edge

    return {"nodes": list(nodes.values()), "edges": list(edges.values())}


def load_article_text(md_path: Path, max_chars: int | None = None) -> str:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    if max_chars and len(text) > max_chars:
        return text[:max_chars]
    return text


def run_single_prompt(prompt_path: Path, article_text: str, model: str, api_key: str, api_url: str) -> tuple[dict[str, Any], str, float]:
    prompt_text = load_prompt_text(prompt_path)
    final_prompt = prepare_prompt(prompt_text, article_text)
    start = time.perf_counter()
    raw = call_openai(final_prompt, model=model, api_key=api_key, api_url=api_url)
    elapsed = time.perf_counter() - start
    return parse_json_response(raw), raw, elapsed


def run_staged_prompt_suite(
    article_text: str,
    model: str,
    api_key: str,
    api_url: str,
    synthesis_prompt: Path,
    testing_prompt: Path,
    characterization_prompt: Path,
    missing_check_prompt: Path | None = None,
) -> tuple[dict[str, Any], dict[str, str], float]:
    raws: dict[str, str] = {}
    total_elapsed = 0.0

    synthesis_text = load_prompt_text(synthesis_prompt)
    start = time.perf_counter()
    synthesis_raw = call_openai(prepare_prompt(synthesis_text, article_text), model=model, api_key=api_key, api_url=api_url)
    total_elapsed += time.perf_counter() - start
    raws["synthesis"] = synthesis_raw
    synthesis_graph = parse_json_response(synthesis_raw)
    catalyst_ids = _ensure_list_of_strings(synthesis_graph.get("catalyst_tested_ids"))

    testing_text = load_prompt_text(testing_prompt)
    start = time.perf_counter()
    testing_raw = call_openai(prepare_prompt(testing_text, article_text, catalyst_ids=catalyst_ids), model=model, api_key=api_key, api_url=api_url)
    total_elapsed += time.perf_counter() - start
    raws["testing"] = testing_raw
    testing_graph = parse_json_response(testing_raw)

    characterization_text = load_prompt_text(characterization_prompt)
    start = time.perf_counter()
    characterization_raw = call_openai(prepare_prompt(characterization_text, article_text, catalyst_ids=catalyst_ids), model=model, api_key=api_key, api_url=api_url)
    total_elapsed += time.perf_counter() - start
    raws["characterization"] = characterization_raw
    characterization_graph = parse_json_response(characterization_raw)

    merged = merge_graphs([synthesis_graph, testing_graph, characterization_graph])

    if missing_check_prompt is not None:
        review_text = load_prompt_text(missing_check_prompt)
        start = time.perf_counter()
        review_raw = call_openai(prepare_prompt(review_text, article_text, initial_graph=merged), model=model, api_key=api_key, api_url=api_url)
        total_elapsed += time.perf_counter() - start
        raws["missing_check"] = review_raw
        review_graph = parse_json_response(review_raw)
        merged = apply_missing_check(merged, review_graph)

    return merged, raws, total_elapsed


def summarize_run(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    success = sum(1 for item in results if item.get("success"))
    parse_fail = total - success

    def avg(key: str) -> float:
        vals = [float(item[key]) for item in results if item.get("success") and isinstance(item.get(key), (int, float))]
        return sum(vals) / len(vals) if vals else 0.0

    def rate(flag: str) -> float:
        vals = [1 for item in results if item.get("success") and item.get("summary", {}).get(flag)]
        denom = sum(1 for item in results if item.get("success"))
        return len(vals) / denom if denom else 0.0

    return {
        "total": total,
        "success": success,
        "parse_fail": parse_fail,
        "success_rate": success / total if total else 0.0,
        "avg_latency_s": avg("latency_s"),
        "avg_nodes": avg("nodes"),
        "avg_edges": avg("edges"),
        "paper_rate": rate("has_paper"),
        "catalyst_rate": rate("has_catalyst"),
        "poisoned_catalyst_rate": rate("has_poisoned_catalyst"),
        "preparation_rate": rate("has_preparation"),
        "testing_rate": rate("has_testing"),
        "characterization_rate": rate("has_characterization"),
    }


def run_eval(
    md_dir: Path,
    out_dir: Path,
    model: str,
    sample_size: int,
    seed: int,
    api_key: str | None = None,
    api_url: str = DEFAULT_API_URL,
    max_chars: int | None = 24000,
    include_missing_check: bool = False,
) -> dict[str, Any]:
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    out_dir.mkdir(parents=True, exist_ok=True)
    samples = sample_markdown_files(md_dir, sample_size=sample_size, seed=seed)

    prompt_root = REPO_ROOT / "prompt" / "map"

    profiles = {
        "compact_100": {"type": "single", "prompt": prompt_root / "v003_nh3_map_graph_abstract_prompt_100.md"},
        "staged_v005": {
            "type": "staged",
            "synthesis": prompt_root / "v005_nh3_map_synthesis_prompt.md",
            "testing": prompt_root / "v005_nh3_map_testing_prompt.md",
            "characterization": prompt_root / "v005_nh3_map_characterization_prompt.md",
            "missing_check": prompt_root / "v005_nh3_map_missing_check_prompt.md",
        },
        "archive_compact_50": {"type": "single", "prompt": REPO_ROOT / "prompt" / "archive" / "map" / "v002_nh3_map_graph_abstract_prompt_50.md"},
        "archive_staged_v004": {
            "type": "staged",
            "synthesis": REPO_ROOT / "prompt" / "archive" / "map" / "v004_nh3_map_synthesis_prompt.md",
            "testing": REPO_ROOT / "prompt" / "archive" / "map" / "v004_nh3_map_testing_prompt.md",
            "characterization": REPO_ROOT / "prompt" / "archive" / "map" / "v004_nh3_map_characterization_prompt.md",
            "missing_check": REPO_ROOT / "prompt" / "archive" / "map" / "v004_nh3_map_missing_check_prompt.md",
        },
    }

    selected_path = out_dir / "selected_files.json"
    selected_path.write_text(json.dumps([p.name for p in samples], ensure_ascii=False, indent=2), encoding="utf-8")

    run_summary: dict[str, Any] = {
        "model": model,
        "sample_size": sample_size,
        "seed": seed,
        "selected_files": [p.name for p in samples],
        "profiles": {},
    }

    for profile_name, profile in profiles.items():
        profile_dir = out_dir / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_results: list[dict[str, Any]] = []

        for md_path in samples:
            article_text = load_article_text(md_path, max_chars=max_chars)
            result: dict[str, Any] = {
                "file": md_path.name,
                "success": False,
            }
            try:
                if profile["type"] == "single":
                    graph, raw, elapsed = run_single_prompt(profile["prompt"], article_text, model=model, api_key=api_key, api_url=api_url)
                    raws = {"single": raw}
                else:
                    graph, raws, elapsed = run_staged_prompt_suite(
                        article_text=article_text,
                        model=model,
                        api_key=api_key,
                        api_url=api_url,
                        synthesis_prompt=profile["synthesis"],
                        testing_prompt=profile["testing"],
                        characterization_prompt=profile["characterization"],
                        missing_check_prompt=profile["missing_check"] if include_missing_check else None,
                    )

                summary = summarize_graph(graph)
                result.update(
                    {
                        "success": True,
                        "latency_s": round(elapsed, 3),
                        "nodes": summary["nodes"],
                        "edges": summary["edges"],
                        "summary": summary,
                    }
                )

                case_dir = profile_dir / md_path.stem
                case_dir.mkdir(parents=True, exist_ok=True)
                (case_dir / "graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
                (case_dir / "metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                for raw_name, raw_text in raws.items():
                    (case_dir / f"{raw_name}_raw.txt").write_text(raw_text, encoding="utf-8")
            except Exception as exc:
                result["error"] = f"{type(exc).__name__}: {exc}"

            profile_results.append(result)

        profile_summary = summarize_run(profile_results)
        run_summary["profiles"][profile_name] = {
            "summary": profile_summary,
            "results": profile_results,
        }
        (profile_dir / "summary.json").write_text(json.dumps({"summary": profile_summary, "results": profile_results}, ensure_ascii=False, indent=2), encoding="utf-8")

    (out_dir / "eval_summary.json").write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return run_summary
