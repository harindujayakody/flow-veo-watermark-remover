#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator, Optional

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm"}
OUT_W = 720
OUT_H = 1280
DEFAULT_ZOOM = 1.12

console = Console()


def clear_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def has_cmd(name: str) -> bool:
    return shutil.which(name) is not None


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def ffprobe_json(video_path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        str(video_path),
    ]
    cp = run(cmd)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or f"ffprobe failed for {video_path}")
    return json.loads(cp.stdout)


def get_video_info(video_path: Path) -> tuple[int, int, float]:
    data = ffprobe_json(video_path)
    stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not stream:
        raise RuntimeError(f"No video stream found in {video_path}")

    width = int(stream["width"])
    height = int(stream["height"])

    duration = 0.0
    if stream.get("duration"):
        duration = float(stream["duration"])
    elif data.get("format", {}).get("duration"):
        duration = float(data["format"]["duration"])

    return width, height, duration


def even(n: int) -> int:
    return n if n % 2 == 0 else n - 1


def format_seconds(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def format_bytes(num: int) -> str:
    step = 1024.0
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num)
    for unit in units:
        if value < step or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= step
    return f"{num} B"


def iter_videos(root: Path, output_root: Path) -> Iterator[Path]:
    out_resolved = output_root.resolve()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in VIDEO_EXTS:
            continue
        try:
            if out_resolved in p.resolve().parents:
                continue
        except Exception:
            pass
        yield p


def recommend_zoom(width: int, height: int, zoom: float) -> str:
    if width == OUT_W and height == OUT_H:
        return f"Already {OUT_W}x{OUT_H} • Zoom {zoom:.2f}x"
    return f"Recommended output: {OUT_W}x{OUT_H} • Zoom {zoom:.2f}x"


def build_zoom_filter(in_w: int, in_h: int, zoom: float) -> str:
    src_ar = in_w / in_h
    dst_ar = OUT_W / OUT_H

    if src_ar > dst_ar:
        base_h = OUT_H
        base_w = even(int(round(base_h * src_ar)))
    else:
        base_w = OUT_W
        base_h = even(int(round(base_w / src_ar)))

    zoom_w = even(int(round(base_w * zoom)))
    zoom_h = even(int(round(base_h * zoom)))

    crop_x = max(0, even((zoom_w - OUT_W) // 2))
    crop_y = max(0, even((zoom_h - OUT_H) // 2))

    return (
        f"scale={base_w}:{base_h}:flags=lanczos,"
        f"scale={zoom_w}:{zoom_h}:flags=lanczos,"
        f"crop={OUT_W}:{OUT_H}:{crop_x}:{crop_y}"
    )


def process_video(video_path: Path, out_path: Path, zoom: float) -> tuple[bool, str]:
    try:
        in_w, in_h, _duration = get_video_info(video_path)
        vf = build_zoom_filter(in_w, in_h, zoom)

        out_path.parent.mkdir(parents=True, exist_ok=True)

        # -n (never overwrite): an existing output fails loudly instead of
        # being silently replaced. The caller confirms the run up front.
        cmd = [
            "ffmpeg",
            "-n",
            "-i",
            str(video_path),
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "copy",
            str(out_path),
        ]
        cp = run(cmd)
        if cp.returncode != 0:
            return False, cp.stderr.strip() or "ffmpeg failed"
        return True, f"Zoom {zoom:.2f}x applied"
    except Exception as e:
        return False, str(e)


def make_hero(input_dir: Path, output_dir: Path, total: int, zoom: float) -> Panel:
    title = Align.center(Text("FLOW VIDEO ZOOM CROP", style="bold white"))
    subtitle = Align.center(Text("Modern terminal dashboard", style="bright_black"))

    info = Table.grid(padding=(0, 2))
    info.add_column(style="cyan", justify="right")
    info.add_column(style="white")
    info.add_row("Input", str(input_dir))
    info.add_row("Output", str(output_dir))
    info.add_row("Videos", str(total))
    info.add_row("Target", f"{OUT_W} x {OUT_H}")
    info.add_row("Zoom", f"{zoom:.2f}x")

    return Panel(
        Group(title, subtitle, Text(""), info),
        border_style="bright_blue",
        padding=(1, 2),
    )


def make_current_task_card(
    current_index: int,
    total: int,
    rel_path: str,
    status: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    duration: Optional[float] = None,
    recommendation: str = "-",
    input_size: Optional[int] = None,
    output_size: Optional[int] = None,
) -> Panel:
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="cyan", justify="right")
    grid.add_column(style="white")

    grid.add_row("Task", f"{current_index}/{total}")
    grid.add_row("File", rel_path)
    grid.add_row("Status", status)

    if width is not None and height is not None:
        grid.add_row("Source", f"{width} x {height}")
    if duration is not None:
        grid.add_row("Duration", format_seconds(duration))
    if input_size is not None:
        grid.add_row("Input Size", format_bytes(input_size))
    if output_size is not None:
        grid.add_row("Output Size", format_bytes(output_size))

    grid.add_row("Recommended", recommendation)

    return Panel(
        grid,
        title="[bold]Current Task[/bold]",
        border_style="magenta",
        padding=(1, 2),
    )


def make_footer(processed: int, failed: int) -> Panel:
    t = Table.grid(padding=(0, 1))
    t.add_column()

    t.add_row(f"[green]Processed:[/green] {processed}")
    t.add_row(f"[red]Failed:[/red] {failed}")
    t.add_row("[bold]Made with love by Harindu[/bold]")
    t.add_row("[bold]Credits[/bold]  Harindu Jayakody")
    t.add_row("[blue]https://github.com/harindujayakody/flow-veo-watermark-remover[/blue]")
    t.add_row("[bright_black]Tip: use JetBrains Mono / Cascadia Code / Fira Code in your terminal[/bright_black]")

    return Panel(t, border_style="bright_black", padding=(0, 2))


def make_summary_panel(
    total: int,
    processed: int,
    failed: int,
    duration: float,
    zoom: float,
    output_dir: Path,
    total_input_bytes: int,
    total_output_bytes: int,
    elapsed: float,
) -> Group:
    success_rate = (processed / total * 100.0) if total else 0.0
    saved = total_input_bytes - total_output_bytes

    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="cyan", justify="right")
    stats.add_column(style="white")

    stats.add_row("Videos Found", str(total))
    stats.add_row("Processed", f"[green]{processed}[/green]")
    stats.add_row("Failed", f"[red]{failed}[/red]")
    stats.add_row("Success Rate", f"[bold green]{success_rate:.1f}%[/bold green]" if failed == 0 else f"[bold yellow]{success_rate:.1f}%[/bold yellow]")
    stats.add_row("Total Duration", format_seconds(duration))
    stats.add_row("Elapsed Time", format_seconds(elapsed))
    stats.add_row("Zoom Used", f"{zoom:.2f}x")
    stats.add_row("Input Size", format_bytes(total_input_bytes))
    stats.add_row("Output Size", format_bytes(total_output_bytes))
    stats.add_row("Difference", f"[green]{format_bytes(abs(saved))} smaller[/green]" if saved > 0 else f"[yellow]{format_bytes(abs(saved))} larger[/yellow]" if saved < 0 else "No change")
    stats.add_row("Output Folder", str(output_dir))

    if failed == 0:
        status_text = Text("✔ ALL TASKS COMPLETED", style="bold green")
        border = "green"
        subtitle = Text("Everything processed successfully", style="bright_black")
    else:
        status_text = Text("⚠ COMPLETED WITH ERRORS", style="bold yellow")
        border = "yellow"
        subtitle = Text("Some files could not be processed", style="bright_black")

    hero = Panel(
        Align.center(
            Group(
                Text("FLOW VIDEO PROCESSOR", style="bold white"),
                Text("Made with love by Harindu", style="bright_black"),
                Text(""),
                status_text,
                subtitle,
            )
        ),
        border_style=border,
        padding=(1, 2),
    )

    stats_panel = Panel(
        stats,
        title="[bold]Summary[/bold]",
        border_style="bright_blue",
        padding=(1, 2),
    )

    return Group(hero, stats_panel, Rule(style="bright_black"))


def build_screen(
    hero: Panel,
    current_task: Panel,
    progress_renderable,
    footer: Panel,
):
    return Group(
        hero,
        current_task,
        Panel(progress_renderable, title="[bold]Overall Progress[/bold]", border_style="green", padding=(1, 2)),
        footer,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Zoom-crop every video under the current folder to 720x1280.",
        epilog="By default the tool lists what it found and asks for confirmation "
               "before re-encoding anything. Files already at 720x1280 are skipped.",
    )
    parser.add_argument("zoom", nargs="?", type=float, default=DEFAULT_ZOOM,
                        help=f"zoom factor, >= 1.0 (default {DEFAULT_ZOOM})")
    parser.add_argument("--dry-run", action="store_true",
                        help="list the videos that would be processed and exit without changing anything")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="skip the confirmation prompt and process everything found")
    parser.add_argument("--force", action="store_true",
                        help="also re-encode files that are already 720x1280 (normally skipped)")
    args = parser.parse_args(argv)
    if args.zoom < 1.0:
        parser.error("zoom factor must be >= 1.0")
    return args


def main() -> int:
    args = parse_args()
    zoom = args.zoom
    clear_terminal()

    if not has_cmd("ffmpeg") or not has_cmd("ffprobe"):
        console.print("[bold red]Error:[/bold red] ffmpeg and ffprobe must be installed and in PATH.")
        return 1

    input_dir = Path.cwd()
    output_dir = input_dir / "output"

    videos = list(iter_videos(input_dir, output_dir))
    total = len(videos)

    if total == 0:
        console.print("[yellow]No videos found.[/yellow]")
        return 0

    # Plan first, encode second: show exactly what will happen and, unless
    # --yes was given, ask before any file is re-encoded. Already-720x1280
    # files are skipped (they need no zoom-crop) unless --force is passed.
    plan_rows = []
    to_process: list[Path] = []
    for video in videos:
        try:
            w, h, _ = get_video_info(video)
        except Exception:
            w = h = None
        already_target = (w == OUT_W and h == OUT_H)
        action = "skip (already 720x1280)" if already_target and not args.force else "process"
        if action == "process":
            to_process.append(video)
        plan_rows.append((str(video.relative_to(input_dir)), f"{w}x{h}" if w else "unreadable", action))

    plan = Table(title="Planned work — nothing has been changed yet", box=None, show_header=True)
    plan.add_column("File")
    plan.add_column("Size")
    plan.add_column("Action")
    for rel, size, action in plan_rows:
        plan.add_row(rel, size, action)
    console.print(plan)
    console.print(f"[dim]{len(to_process)} of {total} video(s) will be processed; output goes to {output_dir}[/dim]")

    if args.dry_run:
        console.print("[yellow]Dry run — exiting without processing anything.[/yellow]")
        return 0

    if not to_process:
        console.print("[yellow]Nothing to process (all files already 720x1280 — use --force to re-encode them).[/yellow]")
        return 0

    if not args.yes:
        from rich.prompt import Confirm
        if not Confirm.ask(f"Process {len(to_process)} video(s) with zoom {zoom:.2f}x?", default=False):
            console.print("[yellow]Cancelled — no files were changed.[/yellow]")
            return 0

    # From here on, only the confirmed list is processed.
    videos = to_process
    total = len(videos)

    processed = 0
    failed = 0
    total_duration = 0.0
    total_input_bytes = 0
    total_output_bytes = 0
    started_at = time.time()

    hero = make_hero(input_dir, output_dir, total, zoom)
    current_task = make_current_task_card(
        current_index=0,
        total=total,
        rel_path="-",
        status="Ready",
        recommendation=f"Will process {total} video(s)",
    )
    footer = make_footer(processed, failed)

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        expand=True,
    )
    task_id = progress.add_task("Processing videos", total=total)

    with Live(
        build_screen(hero, current_task, progress, footer),
        console=console,
        refresh_per_second=8,
        screen=True,
    ) as live:
        with progress:
            for i, video in enumerate(videos, start=1):
                rel = str(video.relative_to(input_dir))
                input_size = video.stat().st_size if video.exists() else 0
                total_input_bytes += input_size

                current_task = make_current_task_card(
                    current_index=i,
                    total=total,
                    rel_path=rel,
                    status="Reading metadata",
                    recommendation="Analyzing source video",
                    input_size=input_size,
                )
                footer = make_footer(processed, failed)
                live.update(build_screen(hero, current_task, progress, footer))

                try:
                    width, height, duration = get_video_info(video)
                    total_duration += duration
                    recommendation = recommend_zoom(width, height, zoom)

                    current_task = make_current_task_card(
                        current_index=i,
                        total=total,
                        rel_path=rel,
                        status="Processing",
                        width=width,
                        height=height,
                        duration=duration,
                        recommendation=recommendation,
                        input_size=input_size,
                    )
                    footer = make_footer(processed, failed)
                    live.update(build_screen(hero, current_task, progress, footer))

                    out_path = output_dir / video.relative_to(input_dir)
                    out_path = out_path.with_name(
                        out_path.stem + f"_zoom_{zoom:.2f}".replace(".", "_") + out_path.suffix
                    )

                    ok, msg = process_video(video, out_path, zoom)

                    output_size = out_path.stat().st_size if ok and out_path.exists() else None
                    if output_size is not None:
                        total_output_bytes += output_size

                    if ok:
                        processed += 1
                        status = "Done"
                    else:
                        failed += 1
                        status = "Failed"

                    current_task = make_current_task_card(
                        current_index=i,
                        total=total,
                        rel_path=rel,
                        status=f"{status} • {msg[:72]}",
                        width=width,
                        height=height,
                        duration=duration,
                        recommendation=recommendation,
                        input_size=input_size,
                        output_size=output_size,
                    )
                    progress.advance(task_id)
                    footer = make_footer(processed, failed)
                    live.update(build_screen(hero, current_task, progress, footer))
                    time.sleep(0.15)

                except Exception as e:
                    failed += 1
                    current_task = make_current_task_card(
                        current_index=i,
                        total=total,
                        rel_path=rel,
                        status=f"Failed • {str(e)[:72]}",
                        recommendation="Could not read/process file",
                        input_size=input_size,
                    )
                    progress.advance(task_id)
                    footer = make_footer(processed, failed)
                    live.update(build_screen(hero, current_task, progress, footer))
                    time.sleep(0.15)

    elapsed = time.time() - started_at
    clear_terminal()

    console.print(
        make_summary_panel(
            total=total,
            processed=processed,
            failed=failed,
            duration=total_duration,
            zoom=zoom,
            output_dir=output_dir,
            total_input_bytes=total_input_bytes,
            total_output_bytes=total_output_bytes,
            elapsed=elapsed,
        )
    )

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
