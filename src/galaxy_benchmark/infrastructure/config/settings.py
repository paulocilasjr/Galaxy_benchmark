"""Typed settings loaders."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from galaxy_benchmark.domain.models import EnvironmentSnapshot


class GalaxySettings(BaseModel):
    """Galaxy connectivity settings."""

    model_config = ConfigDict(extra="forbid")

    api_key: str = ""
    base_url: str = "https://usegalaxy.org/"


class ModelProviderSettings(BaseModel):
    """External model provider credentials."""

    model_config = ConfigDict(extra="forbid")

    openai_api_key: str = ""
    anthropic_api_key: str = ""


class MCPSettings(BaseModel):
    """MCP adapter settings."""

    model_config = ConfigDict(extra="forbid")

    endpoint: str = ""
    enabled: bool = False


class BenchmarkSettings(BaseModel):
    """Benchmark path settings."""

    model_config = ConfigDict(extra="forbid")

    benchmark_root: Path = Path("benchmark")
    runs_root: Path = Path("runs")
    cache_root: Path = Path(".cache")


class AppSettings(BaseModel):
    """Top-level application settings."""

    model_config = ConfigDict(extra="forbid")

    galaxy: GalaxySettings = Field(default_factory=GalaxySettings)
    providers: ModelProviderSettings = Field(default_factory=ModelProviderSettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    benchmark: BenchmarkSettings = Field(default_factory=BenchmarkSettings)

    @classmethod
    def load(cls, env_path: Path | None = None) -> "AppSettings":
        env = dict(os.environ)
        if env_path and env_path.exists():
            env.update(_parse_dotenv(env_path))
        return cls(
            galaxy=GalaxySettings(
                api_key=env.get("GALAXY_API_KEY", ""),
                base_url=env.get("GALAXY_BASE_URL", "https://usegalaxy.org/"),
            ),
            providers=ModelProviderSettings(
                openai_api_key=env.get("OPENAI_API_KEY", ""),
                anthropic_api_key=env.get("ANTHROPIC_API_KEY", ""),
            ),
            mcp=MCPSettings(
                endpoint=env.get("MCP_ENDPOINT", ""),
                enabled=env.get("MCP_ENABLED", "").lower() in {"1", "true", "yes"},
            ),
            benchmark=BenchmarkSettings(
                benchmark_root=Path(env.get("BENCHMARK_ROOT", "benchmark")),
                runs_root=Path(env.get("RUNS_ROOT", "runs")),
                cache_root=Path(env.get("CACHE_ROOT", ".cache")),
            ),
        )

    def redacted_environment_snapshot(self) -> EnvironmentSnapshot:
        redacted = {
            "GALAXY_BASE_URL": self.galaxy.base_url,
            "MCP_ENABLED": str(self.mcp.enabled).lower(),
            "BENCHMARK_ROOT": str(self.benchmark.benchmark_root),
            "RUNS_ROOT": str(self.benchmark.runs_root),
        }
        if self.galaxy.api_key:
            redacted["GALAXY_API_KEY"] = "***REDACTED***"
        if self.providers.openai_api_key:
            redacted["OPENAI_API_KEY"] = "***REDACTED***"
        if self.providers.anthropic_api_key:
            redacted["ANTHROPIC_API_KEY"] = "***REDACTED***"
        return EnvironmentSnapshot(
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            environment=redacted,
        )


def _parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values
