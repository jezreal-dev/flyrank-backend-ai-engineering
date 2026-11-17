"""Run the eight labelled BE-07 cases against a locally running API."""

import argparse
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_DIR = Path(__file__).resolve().parents[1]
CASES_PATH = Path(__file__).with_name("cases.json")
VALID_CATEGORIES = {"fiction", "nonfiction", "poetry", "comics", "other"}
VALID_FLAGS = {"insufficient_text", "ambiguous_category"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", help="Optional path to save the full JSON run report")
    args = parser.parse_args()

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    results = []
    for case in cases:
        payload = {key: case[key] for key in ("title", "description") if key in case}
        request = Request(
            args.base_url.rstrip("/") + "/enrich",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=45) as response:
                body = json.loads(response.read().decode("utf-8"))
                status = response.status
            schema_ok = (
                set(body) == {"category", "summary", "quality_flags"}
                and body["category"] in VALID_CATEGORIES
                and isinstance(body["summary"], str)
                and 0 < len(body["summary"].split()) <= 30
                and isinstance(body["quality_flags"], list)
                and all(flag in VALID_FLAGS for flag in body["quality_flags"])
            )
            category_ok = schema_ok and body["category"] == case["expected_category"]
            flag_ok = "expected_quality_flag" not in case or (
                schema_ok and case["expected_quality_flag"] in body["quality_flags"]
            )
            result = {
                "id": case["id"],
                "http_status": status,
                "schema_ok": schema_ok,
                "expected_category": case["expected_category"],
                "actual_category": body.get("category"),
                "category_match": category_ok,
                "expected_quality_flag": case.get("expected_quality_flag"),
                "quality_flag_match": flag_ok,
                "response": body,
            }
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            provider_detail = None
            if isinstance(exc, HTTPError):
                try:
                    error_body = json.loads(exc.read().decode("utf-8"))
                    provider_detail = error_body.get("detail") if isinstance(error_body, dict) else None
                except (UnicodeDecodeError, json.JSONDecodeError):
                    provider_detail = None
            result = {
                "id": case["id"],
                "schema_ok": False,
                "category_match": False,
                "quality_flag_match": False,
                "error": str(exc),
                "api_detail": provider_detail,
            }

        results.append(result)
        state = "PASS" if result["schema_ok"] and result["category_match"] and result["quality_flag_match"] else "REVISE"
        print(
            f"{case['id']} {state} "
            f"category={result.get('actual_category', 'ERROR')} "
            f"expected={case['expected_category']} schema={result['schema_ok']} "
            f"error={result.get('api_detail', '')}"
        )

    schema_count = sum(item["schema_ok"] for item in results)
    category_count = sum(item["category_match"] for item in results)
    flag_cases = sum("expected_quality_flag" in case for case in cases)
    flag_count = sum(item["quality_flag_match"] for item, case in zip(results, cases) if "expected_quality_flag" in case)
    report = {
        "case_count": len(cases),
        "schema_passes": schema_count,
        "category_matches": category_count,
        "category_accuracy": category_count / len(cases),
        "quality_flag_cases": flag_cases,
        "quality_flag_matches": flag_count,
        "results": results,
    }
    print(
        f"Summary: schema {schema_count}/{len(cases)}; "
        f"category {category_count}/{len(cases)} ({report['category_accuracy']:.0%}); "
        f"quality flags {flag_count}/{flag_cases}"
    )
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report saved to {output_path}")
    return 0 if schema_count == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
