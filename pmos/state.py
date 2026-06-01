"""State machine and state file management.

Per design.md:
- TaskState: queued/running/review/complete
- Source of truth hierarchy: agent state > orchestrator state > disk/git
- Atomic writes via temp file + rename
- prompt_sha + prompt_dirty captured per sub-task; run_started_at_commit per run
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class TaskState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    REVIEW = "review"
    COMPLETE = "complete"


class SubTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class SubTaskRecord:
    name: str
    status: SubTaskStatus = SubTaskStatus.PENDING
    prompt_sha: str | None = None
    prompt_dirty: bool = False
    output: Any = None
    error: str | None = None


@dataclass
class AgentRunState:
    """One agent's run. Source of truth for that agent's progress."""

    agent_name: str
    run_id: str
    task_state: TaskState = TaskState.QUEUED
    sub_tasks: list[SubTaskRecord] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    judgment_log: list[dict[str, Any]] = field(default_factory=list)
    started_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "run_id": self.run_id,
            "task_state": self.task_state.value,
            "sub_tasks": [
                {
                    "name": st.name,
                    "status": st.status.value,
                    "prompt_sha": st.prompt_sha,
                    "prompt_dirty": st.prompt_dirty,
                    "output": st.output,
                    "error": st.error,
                }
                for st in self.sub_tasks
            ],
            "inputs": self.inputs,
            "judgment_log": self.judgment_log,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AgentRunState:
        return cls(
            agent_name=data["agent_name"],
            run_id=data["run_id"],
            task_state=TaskState(data["task_state"]),
            sub_tasks=[
                SubTaskRecord(
                    name=st["name"],
                    status=SubTaskStatus(st["status"]),
                    prompt_sha=st.get("prompt_sha"),
                    prompt_dirty=st.get("prompt_dirty", False),
                    output=st.get("output"),
                    error=st.get("error"),
                )
                for st in data.get("sub_tasks", [])
            ],
            inputs=data.get("inputs", {}),
            judgment_log=data.get("judgment_log", []),
            started_at=data.get("started_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def save(self, base_dir: Path) -> None:
        self.updated_at = now_iso()
        atomic_write_json(agent_state_path(base_dir, self.agent_name, self.run_id), self.to_dict())

    @classmethod
    def load(cls, base_dir: Path, agent_name: str, run_id: str) -> AgentRunState:
        return cls.from_dict(read_json(agent_state_path(base_dir, agent_name, run_id)))


@dataclass
class OrchestratorState:
    """Pipeline-level state. Tracks which agent is active and run-level metadata."""

    run_id: str
    run_started_at_commit: str = ""
    active_agent: str | None = None
    active_task_state: TaskState | None = None
    updated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "run_started_at_commit": self.run_started_at_commit,
            "active_agent": self.active_agent,
            "active_task_state": self.active_task_state.value if self.active_task_state else None,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> OrchestratorState:
        return cls(
            run_id=data["run_id"],
            run_started_at_commit=data.get("run_started_at_commit", ""),
            active_agent=data.get("active_agent"),
            active_task_state=(
                TaskState(data["active_task_state"]) if data.get("active_task_state") else None
            ),
            updated_at=data.get("updated_at", ""),
        )

    def save(self, base_dir: Path) -> None:
        self.updated_at = now_iso()
        atomic_write_json(orchestrator_state_path(base_dir), self.to_dict())

    @classmethod
    def load(cls, base_dir: Path) -> OrchestratorState:
        return cls.from_dict(read_json(orchestrator_state_path(base_dir)))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, data: dict) -> None:
    """Write JSON via temp file + rename. Crash-safe on POSIX."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def read_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def agent_state_path(base_dir: Path, agent_name: str, run_id: str) -> Path:
    return Path(base_dir) / "_system" / "agent-state" / f"{agent_name}-{run_id}.json"


def orchestrator_state_path(base_dir: Path) -> Path:
    return Path(base_dir) / "_system" / "orchestrator" / "current-state.json"
