from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings


class WoobeRuntimeError(RuntimeError):
    pass


async def run_atlas_network(
    *,
    assessment_id: str,
    required_domains: list[str],
    idempotency_key: str,
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.woobe_runtime_key:
        raise WoobeRuntimeError("WOOBE_RUNTIME_KEY is not configured.")

    message = (
        "Execute an Atlas vendor-risk assessment. "
        f"assessment_id={assessment_id}. "
        f"Required domains: {', '.join(required_domains)}. "
        "Obtain case facts only through the Atlas HTTP Tools. "
        "Use the Woobe Knowledge attached to each Agent as assessment policy, "
        "never as evidence about this vendor. Delegate the required specialist analyses "
        "and return the final result strictly according to the configured output contract."
    )

    payload = {
        "message": message,
        "tenant_id": "atlas-demo",
        "user_id": "atlas-backend",
        "metadata": {
            "product": "atlas",
            "assessment_id": assessment_id,
            "required_domains": required_domains,
        },
        "idempotency_key": idempotency_key,
    }

    headers = {
        "Authorization": f"Bearer {settings.woobe_runtime_key}",
        "Content-Type": "application/json",
    }

    url = f"{settings.woobe_base_url.rstrip('/')}/v1/run"
    try:
        async with httpx.AsyncClient(timeout=settings.woobe_timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
    except httpx.HTTPError as exc:
        raise WoobeRuntimeError(f"Woobe Runtime API unavailable: {exc}") from exc

    try:
        body = response.json()
    except ValueError as exc:
        raise WoobeRuntimeError(
            f"Woobe returned HTTP {response.status_code} with a non-JSON response."
        ) from exc

    if response.status_code >= 400 or not body.get("success"):
        message = body.get("message") or f"Woobe runtime failed with HTTP {response.status_code}."
        raise WoobeRuntimeError(str(message))

    data = body.get("data") or {}
    result = data.get("parsed_output")
    if result is None:
        result = data.get("result")
    if not isinstance(result, dict):
        raise WoobeRuntimeError(
            "Atlas expects the Network Release to have structured output enabled."
        )

    return {
        "result": result,
        "execution_id": data.get("execution_id") or data.get("job_id"),
        "session_id": data.get("session_id"),
        "trace_id": data.get("trace_id"),
        "network_version_id": data.get("network_version_id"),
    }
