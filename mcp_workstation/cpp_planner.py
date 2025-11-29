"""
MCP Workstation - C++ Transition Planner

Plans and tracks the transition from Python to C++ for the professional DAW.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

from .models import PhaseStatus, AIAgent
from .debug import get_debug, DebugCategory, trace
from .ai_specializations import TaskType, get_best_agent_for_task


class CppPriority(str, Enum):
    """Priority levels for C++ porting."""
    CRITICAL = "critical"      # Real-time DSP, must be C++
    HIGH = "high"              # Performance-sensitive
    MEDIUM = "medium"          # Nice to have in C++
    LOW = "low"                # Can stay Python
    OPTIONAL = "optional"      # Port only if needed


class PortingStrategy(str, Enum):
    """Strategies for porting Python to C++."""
    REWRITE = "rewrite"                # Full rewrite in C++
    PYBIND11 = "pybind11"              # Keep Python API, C++ core
    CYTHON = "cython"                  # Cython for critical paths
    HYBRID = "hybrid"                  # Mix of approaches
    KEEP_PYTHON = "keep_python"        # Don't port


@dataclass
class CppModule:
    """A C++ module to be created."""
    id: str
    name: str
    description: str
    python_source: str              # Original Python module path
    cpp_target: str                 # Target C++ file path
    priority: CppPriority = CppPriority.MEDIUM
    strategy: PortingStrategy = PortingStrategy.PYBIND11
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    progress: float = 0.0

    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other module IDs
    cpp_dependencies: List[str] = field(default_factory=list)  # C++ libs

    # Technical details
    estimated_loc: int = 0          # Estimated lines of C++ code
    requires_simd: bool = False     # Needs SIMD optimization
    requires_gpu: bool = False      # Needs GPU/CUDA
    real_time_safe: bool = False    # Must be real-time safe

    # Assignment
    assigned_to: Optional[AIAgent] = None
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "python_source": self.python_source,
            "cpp_target": self.cpp_target,
            "priority": self.priority.value,
            "strategy": self.strategy.value,
            "status": self.status.value,
            "progress": self.progress,
            "depends_on": self.depends_on,
            "cpp_dependencies": self.cpp_dependencies,
            "estimated_loc": self.estimated_loc,
            "requires_simd": self.requires_simd,
            "requires_gpu": self.requires_gpu,
            "real_time_safe": self.real_time_safe,
            "assigned_to": self.assigned_to.value if self.assigned_to else None,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CppModule":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            python_source=data.get("python_source", ""),
            cpp_target=data.get("cpp_target", ""),
            priority=CppPriority(data.get("priority", "medium")),
            strategy=PortingStrategy(data.get("strategy", "pybind11")),
            status=PhaseStatus(data.get("status", "not_started")),
            progress=data.get("progress", 0.0),
            depends_on=data.get("depends_on", []),
            cpp_dependencies=data.get("cpp_dependencies", []),
            estimated_loc=data.get("estimated_loc", 0),
            requires_simd=data.get("requires_simd", False),
            requires_gpu=data.get("requires_gpu", False),
            real_time_safe=data.get("real_time_safe", False),
            assigned_to=AIAgent(data["assigned_to"]) if data.get("assigned_to") else None,
            notes=data.get("notes", ""),
        )


@dataclass
class CppTask:
    """A specific task within C++ development."""
    id: str
    module_id: str
    name: str
    task_type: TaskType
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    assigned_to: Optional[AIAgent] = None
    estimated_hours: float = 0.0
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "module_id": self.module_id,
            "name": self.name,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "assigned_to": self.assigned_to.value if self.assigned_to else None,
            "estimated_hours": self.estimated_hours,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CppTask":
        return cls(
            id=data["id"],
            module_id=data["module_id"],
            name=data["name"],
            task_type=TaskType(data["task_type"]),
            status=PhaseStatus(data.get("status", "not_started")),
            assigned_to=AIAgent(data["assigned_to"]) if data.get("assigned_to") else None,
            estimated_hours=data.get("estimated_hours", 0.0),
            notes=data.get("notes", ""),
        )


# =============================================================================
# Default C++ Module Plan for iDAW
# =============================================================================

IDAW_CPP_MODULES = [
    CppModule(
        id="cpp_core",
        name="libdaiw-core",
        description="Core C++ library with fundamental types and utilities",
        python_source="music_brain/",
        cpp_target="cpp/src/core/",
        priority=CppPriority.CRITICAL,
        strategy=PortingStrategy.REWRITE,
        estimated_loc=2000,
        cpp_dependencies=["fmt", "spdlog"],
    ),
    CppModule(
        id="cpp_midi",
        name="MIDI Engine",
        description="High-performance MIDI processing and groove application",
        python_source="music_brain/groove/",
        cpp_target="cpp/src/midi/",
        priority=CppPriority.CRITICAL,
        strategy=PortingStrategy.REWRITE,
        estimated_loc=3000,
        requires_simd=True,
        real_time_safe=True,
        depends_on=["cpp_core"],
        cpp_dependencies=["rtmidi"],
    ),
    CppModule(
        id="cpp_dsp",
        name="DSP Module",
        description="Real-time digital signal processing",
        python_source="music_brain/audio/",
        cpp_target="cpp/src/dsp/",
        priority=CppPriority.CRITICAL,
        strategy=PortingStrategy.REWRITE,
        estimated_loc=5000,
        requires_simd=True,
        real_time_safe=True,
        depends_on=["cpp_core"],
        cpp_dependencies=["fftw3", "kissfft"],
    ),
    CppModule(
        id="cpp_harmony",
        name="Harmony Analysis",
        description="Chord detection, key analysis, progression analysis",
        python_source="music_brain/structure/",
        cpp_target="cpp/src/harmony/",
        priority=CppPriority.HIGH,
        strategy=PortingStrategy.PYBIND11,
        estimated_loc=2500,
        depends_on=["cpp_core"],
    ),
    CppModule(
        id="cpp_groove",
        name="Groove Templates",
        description="Genre groove templates and application",
        python_source="music_brain/groove/templates.py",
        cpp_target="cpp/src/groove/",
        priority=CppPriority.HIGH,
        strategy=PortingStrategy.PYBIND11,
        estimated_loc=1500,
        real_time_safe=True,
        depends_on=["cpp_core", "cpp_midi"],
    ),
    CppModule(
        id="cpp_intent",
        name="Intent Processor",
        description="Song intent schema processing",
        python_source="music_brain/session/intent_processor.py",
        cpp_target="cpp/src/intent/",
        priority=CppPriority.MEDIUM,
        strategy=PortingStrategy.KEEP_PYTHON,  # Complex, not real-time
        estimated_loc=0,
    ),
    CppModule(
        id="cpp_vst",
        name="VST3 Plugin",
        description="VST3 plugin wrapper using JUCE",
        python_source="",  # New development
        cpp_target="cpp/src/plugin/vst3/",
        priority=CppPriority.CRITICAL,
        strategy=PortingStrategy.REWRITE,
        estimated_loc=4000,
        real_time_safe=True,
        depends_on=["cpp_core", "cpp_dsp", "cpp_midi"],
        cpp_dependencies=["JUCE", "VST3 SDK"],
    ),
    CppModule(
        id="cpp_au",
        name="Audio Unit Plugin",
        description="macOS Audio Unit wrapper",
        python_source="",
        cpp_target="cpp/src/plugin/au/",
        priority=CppPriority.HIGH,
        strategy=PortingStrategy.REWRITE,
        estimated_loc=2000,
        real_time_safe=True,
        depends_on=["cpp_core", "cpp_dsp", "cpp_midi"],
        cpp_dependencies=["JUCE", "CoreAudio"],
    ),
    CppModule(
        id="cpp_gui",
        name="Plugin GUI",
        description="JUCE-based plugin GUI",
        python_source="",
        cpp_target="cpp/src/gui/",
        priority=CppPriority.HIGH,
        strategy=PortingStrategy.REWRITE,
        estimated_loc=6000,
        depends_on=["cpp_vst"],
        cpp_dependencies=["JUCE"],
    ),
    CppModule(
        id="cpp_python_bridge",
        name="Python Bridge",
        description="pybind11 bindings for Python access",
        python_source="",
        cpp_target="cpp/src/python/",
        priority=CppPriority.MEDIUM,
        strategy=PortingStrategy.PYBIND11,
        estimated_loc=1500,
        depends_on=["cpp_core", "cpp_midi", "cpp_dsp", "cpp_harmony"],
        cpp_dependencies=["pybind11"],
    ),
]


# =============================================================================
# C++ Transition Planner
# =============================================================================

class CppTransitionPlanner:
    """
    Plans and tracks the Python to C++ transition for DAiW.

    Features:
    - Module dependency tracking
    - Task generation and assignment
    - Progress tracking
    - Build system planning
    """

    def __init__(self, modules: Optional[List[CppModule]] = None):
        self.modules: Dict[str, CppModule] = {}
        self.tasks: Dict[str, CppTask] = {}
        self._debug = get_debug()

        # Initialize with default modules or provided
        if modules:
            for mod in modules:
                self.modules[mod.id] = mod
        else:
            for mod in IDAW_CPP_MODULES:
                self.modules[mod.id] = CppModule.from_dict(mod.to_dict())

    @trace(DebugCategory.PHASE)
    def get_module(self, module_id: str) -> Optional[CppModule]:
        """Get a module by ID."""
        return self.modules.get(module_id)

    @trace(DebugCategory.PHASE)
    def get_ready_modules(self) -> List[CppModule]:
        """Get modules that are ready to start (dependencies met)."""
        ready = []
        for mod in self.modules.values():
            if mod.status != PhaseStatus.NOT_STARTED:
                continue  # Already started

            # Check dependencies
            deps_met = True
            for dep_id in mod.depends_on:
                dep = self.modules.get(dep_id)
                if not dep or dep.status not in (PhaseStatus.COMPLETED, PhaseStatus.VERIFIED):
                    deps_met = False
                    break

            if deps_met:
                ready.append(mod)

        # Sort by priority
        priority_order = {
            CppPriority.CRITICAL: 0,
            CppPriority.HIGH: 1,
            CppPriority.MEDIUM: 2,
            CppPriority.LOW: 3,
            CppPriority.OPTIONAL: 4,
        }
        ready.sort(key=lambda m: priority_order.get(m.priority, 5))

        return ready

    @trace(DebugCategory.PHASE)
    def start_module(self, module_id: str, agent: Optional[AIAgent] = None):
        """Start work on a module."""
        mod = self.modules.get(module_id)
        if not mod:
            return

        mod.status = PhaseStatus.IN_PROGRESS
        if agent:
            mod.assigned_to = agent

        # Generate tasks for this module
        self._generate_module_tasks(mod)

        self._debug.info(
            DebugCategory.PHASE,
            f"Started C++ module: {mod.name}",
            data={"module_id": module_id, "strategy": mod.strategy.value},
        )

    def _generate_module_tasks(self, module: CppModule):
        """Generate standard tasks for a module."""
        task_templates = [
            (f"{module.id}_design", "Design C++ API", TaskType.API_DESIGN),
            (f"{module.id}_impl", "Implement C++ code", TaskType.CPP_DEVELOPMENT),
            (f"{module.id}_test", "Write unit tests", TaskType.TESTING),
            (f"{module.id}_optimize", "Optimize performance", TaskType.LOW_LEVEL_OPTIMIZATION),
            (f"{module.id}_docs", "Write documentation", TaskType.DOCUMENTATION),
        ]

        if module.strategy == PortingStrategy.PYBIND11:
            task_templates.append(
                (f"{module.id}_bindings", "Create pybind11 bindings", TaskType.CPP_DEVELOPMENT)
            )

        if module.requires_simd:
            task_templates.append(
                (f"{module.id}_simd", "SIMD optimization", TaskType.LOW_LEVEL_OPTIMIZATION)
            )

        for task_id, name, task_type in task_templates:
            if task_id not in self.tasks:
                task = CppTask(
                    id=task_id,
                    module_id=module.id,
                    name=name,
                    task_type=task_type,
                    assigned_to=get_best_agent_for_task(task_type),
                )
                self.tasks[task_id] = task

    @trace(DebugCategory.PHASE)
    def update_module_progress(
        self,
        module_id: str,
        progress: float,
        status: Optional[PhaseStatus] = None,
    ):
        """Update module progress."""
        mod = self.modules.get(module_id)
        if not mod:
            return

        mod.progress = min(1.0, max(0.0, progress))

        if status:
            mod.status = status
        elif progress >= 1.0:
            mod.status = PhaseStatus.COMPLETED

        self._debug.info(
            DebugCategory.PHASE,
            f"Module {mod.name} progress: {progress:.0%}",
        )

    def get_progress_summary(self) -> Dict:
        """Get overall C++ transition progress."""
        total_loc = sum(m.estimated_loc for m in self.modules.values())
        completed_loc = sum(
            m.estimated_loc * m.progress
            for m in self.modules.values()
        )

        by_priority = {}
        for mod in self.modules.values():
            p = mod.priority.value
            if p not in by_priority:
                by_priority[p] = {"total": 0, "completed": 0}
            by_priority[p]["total"] += 1
            if mod.status == PhaseStatus.COMPLETED:
                by_priority[p]["completed"] += 1

        return {
            "total_modules": len(self.modules),
            "modules_completed": sum(
                1 for m in self.modules.values()
                if m.status == PhaseStatus.COMPLETED
            ),
            "modules_in_progress": sum(
                1 for m in self.modules.values()
                if m.status == PhaseStatus.IN_PROGRESS
            ),
            "estimated_total_loc": total_loc,
            "estimated_completed_loc": int(completed_loc),
            "overall_progress": completed_loc / total_loc if total_loc > 0 else 0,
            "by_priority": by_priority,
            "ready_to_start": [m.id for m in self.get_ready_modules()],
        }

    def get_dependency_order(self) -> List[str]:
        """Get modules in dependency order (topological sort)."""
        visited = set()
        order = []

        def visit(mod_id: str):
            if mod_id in visited:
                return
            visited.add(mod_id)
            mod = self.modules.get(mod_id)
            if mod:
                for dep_id in mod.depends_on:
                    visit(dep_id)
                order.append(mod_id)

        for mod_id in self.modules:
            visit(mod_id)

        return order

    def get_build_plan(self) -> str:
        """Generate a CMakeLists.txt plan."""
        lines = [
            "# DAiW C++ Build Plan",
            "# Auto-generated by MCP Workstation",
            "",
            "cmake_minimum_required(VERSION 3.20)",
            "project(DAiW VERSION 1.0.0 LANGUAGES CXX)",
            "",
            "set(CMAKE_CXX_STANDARD 20)",
            "set(CMAKE_CXX_STANDARD_REQUIRED ON)",
            "",
            "# Dependencies",
        ]

        # Collect all dependencies
        all_deps = set()
        for mod in self.modules.values():
            all_deps.update(mod.cpp_dependencies)

        for dep in sorted(all_deps):
            if dep == "JUCE":
                lines.append("find_package(JUCE CONFIG REQUIRED)")
            elif dep == "pybind11":
                lines.append("find_package(pybind11 CONFIG REQUIRED)")
            else:
                lines.append(f"find_package({dep} REQUIRED)")

        lines.extend(["", "# Modules"])

        # Add modules in dependency order
        for mod_id in self.get_dependency_order():
            mod = self.modules.get(mod_id)
            if not mod or mod.strategy == PortingStrategy.KEEP_PYTHON:
                continue

            lines.extend([
                "",
                f"# {mod.name}",
                f"add_library({mod.id}",
                f"    {mod.cpp_target}/*.cpp",
                ")",
            ])

            if mod.depends_on:
                deps_str = " ".join(mod.depends_on)
                lines.append(f"target_link_libraries({mod.id} PRIVATE {deps_str})")

        return "\n".join(lines)

    # Serialization
    def to_dict(self) -> Dict:
        return {
            "modules": {mid: m.to_dict() for mid, m in self.modules.items()},
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CppTransitionPlanner":
        modules = [CppModule.from_dict(m) for m in data.get("modules", {}).values()]
        planner = cls(modules=modules)

        for tid, tdata in data.get("tasks", {}).items():
            planner.tasks[tid] = CppTask.from_dict(tdata)

        return planner


# =============================================================================
# Display Functions
# =============================================================================

def format_cpp_plan(planner: CppTransitionPlanner) -> str:
    """Format the C++ transition plan for display."""
    lines = [
        "=" * 60,
        "C++ TRANSITION PLAN - DAiW Professional DAW",
        "=" * 60,
        "",
    ]

    summary = planner.get_progress_summary()
    lines.extend([
        f"Overall Progress: {summary['overall_progress']:.0%}",
        f"Modules: {summary['modules_completed']}/{summary['total_modules']} completed",
        f"Estimated Code: {summary['estimated_completed_loc']:,}/{summary['estimated_total_loc']:,} LOC",
        "",
        "MODULES:",
    ])

    priority_order = ["critical", "high", "medium", "low", "optional"]

    for priority in priority_order:
        mods = [m for m in planner.modules.values() if m.priority.value == priority]
        if not mods:
            continue

        lines.append(f"\n[{priority.upper()}]")

        for mod in mods:
            status_icon = {
                PhaseStatus.NOT_STARTED: "○",
                PhaseStatus.IN_PROGRESS: "◐",
                PhaseStatus.BLOCKED: "✗",
                PhaseStatus.COMPLETED: "●",
                PhaseStatus.VERIFIED: "✓",
            }.get(mod.status, "?")

            progress_bar = "█" * int(mod.progress * 10) + "░" * (10 - int(mod.progress * 10))
            assigned = f" [{mod.assigned_to.value}]" if mod.assigned_to else ""

            lines.append(f"  {status_icon} {mod.name}{assigned}")
            lines.append(f"    [{progress_bar}] {mod.progress:.0%} | {mod.strategy.value}")
            lines.append(f"    {mod.cpp_target}")

            if mod.depends_on:
                lines.append(f"    Depends: {', '.join(mod.depends_on)}")

    if summary["ready_to_start"]:
        lines.extend([
            "",
            "READY TO START:",
            *[f"  • {mid}" for mid in summary["ready_to_start"]],
        ])

    return "\n".join(lines)
