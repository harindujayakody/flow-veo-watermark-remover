#!/usr/bin/env python3
"""
Flow Video Zoom Crop
Author: Harindu Jayakody
Website: https://infiax.com

Batch video crop and zoom utility for vertical mobile formats.
"""

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
from rich.prompt import Confirm
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
            if out_resolved in p.resolve().parents or p.resolve() == out_resolved:
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

        cmd = [
            "ffmpeg",
            "-y",
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
        border_style="cyan",
        padding=(1, 2),
    )


def make_current_task_card(
    current_index: int,
    total: int,
    rel_path: str,
    status: str,
    recommendation: str = "",
    width: Optional[int] = None,
    height: Optional[int] = None,
    duration: Optional[float] = None,
    input_size: Optional[int] = None,
    output_size: Optional[int] = None,
) -> Panel:
    title = f"[bold cyan]Current Video[/bold cyan] [bright_black]({current_index}/{total})[/bright_black]"

    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", justify="right", width=14)
    table.add_column(style="white")

    table.add_row("File", rel_path)
    table.add_row("Status", status)

    if width and height:
        table.add_row("Resolution", f"{width}x{height} -> {OUT_W}x{OUT_H}")
    if duration is not None:
        table.add_row("Duration", format_seconds(duration))
    if input_size is not None:
        table.add_row("Input Size", format_bytes(input_size))
    if output_size is not None:
        table.add_row("Output Size", format_bytes(output_size))
    if recommendation:
        table.add_row("Plan", recommendation)

    return Panel(table, title=title, border_style="blue", padding=(1, 2))


def make_footer(processed: int, failed: int) -> Panel:
    table = Table.grid(expand=True)
    table.add_column(justify="left")
    table.add_column(justify="right")

    left = Text.from_markup(f"[green]Done: {processed}[/green]  |  [red]Failed: {failed}[/red]")
    right = Text.from_markup("[bright_black]Press Ctrl+C to cancel[/bright_black]")

    table.add_row(left, right)
    return Panel(table, border_style="bright_black", padding=(0, 2))


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
    status_text = Text(
        "ALL DONE!" if failed == 0 else "COMPLETED WITH WARNINGS",
        style="bold green" if failed == 0 else "bold yellow",
    )
    subtitle = Text(f"Finished processing in {format_seconds(elapsed)}", style="bright_black")

    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="cyan", justify="right")
    stats.add_column(style="white")

    stats.add_row("Total Videos", str(total))
    stats.add_row("Processed", str(processed))
    stats.add_row("Failed", str(failed))
    stats.add_row("Total Duration", format_seconds(duration))
    stats.add_row("Applied Zoom", f"{zoom:.2f}x")
    stats.add_row("Input Bytes", format_bytes(total_input_bytes))
    stats.add_row("Output Bytes", format_bytes(total_output_bytes))
    stats.add_row("Output Dir", str(output_dir))

    border = "green" if failed == 0 else "yellow"
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


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Flow Video Zoom Crop - Batch process, zoom, and crop videos for vertical formats."
    )
    parser.add_argument(
        "zoom",
        nargs="?",
        type=float,
        default=DEFAULT_ZOOM,
        help=f"Zoom factor (>= 1.0, default: {DEFAULT_ZOOM})",
    )
    parser.add_argument(
        "-i", "--input",
        dest="input_dir",
        type=Path,
        default=Path.cwd(),
        help="Input directory containing videos to process (default: current directory)",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        type=Path,
        default=None,
        help="Output directory for processed videos (default: ./output)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview scanned videos, filter calculations, and plans without modifying or encoding files",
    )
    parser.add_argument(
        "-y", "--yes",
        dest="assume_yes",
        action="store_true",
        help="Skip interactive confirmation prompt before starting encoding",
    )
    parser.add_argument(
        "--skip-processed",
        action="store_true",
        help="Skip videos if their corresponding output file already exists",
    )
    parser.add_argument(
        "--skip-target-res",
        action="store_true",
        help="Skip videos that already match the target resolution (720x1280)",
    )
    return parser.parse_args(args)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    clear_terminal()

    if not has_cmd("ffmpeg") or not has_cmd("ffprobe"):
        console.print("[bold red]Error:[/bold red] ffmpeg and ffprobe must be installed and in PATH.")
        return 1

    zoom = args.zoom
    if zoom < 1.0:
        console.print("[bold red]Error:[/bold red] zoom factor must be >= 1.0")
        return 1

    input_dir = args.input_dir.resolve()
    output_dir = (args.output_dir or (input_dir / "output")).resolve()

    if not input_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Input directory does not exist: {input_dir}")
        return 1

    videos = list(iter_videos(input_dir, output_dir))
    total = len(videos)

    if total == 0:
        console.print("[yellow]No videos found.[/yellow]")
        return 0

    if args.dry_run:
        console.print(Panel(
            f"[bold cyan]DRY-RUN PREVIEW[/bold cyan]\n\nFound [bold]{total}[/bold] video(s) under: [dim]{input_dir}[/dim]\nTarget output: [dim]{output_dir}[/dim]\nResolution: [bold]{OUT_W}x{OUT_H}[/bold] | Zoom: [bold]{zoom:.2f}x[/bold]",
            border_style="cyan",
        ))
        table = Table(title="Planned Videos to Process", border_style="cyan")
        table.add_column("#", justify="right")
        table.add_column("Relative Path")
        table.add_column("Size", justify="right")
        table.add_column("Planned Output")

        for idx, vid in enumerate(videos, start=1):
            rel = vid.relative_to(input_dir)
            out_p = output_dir / rel
            out_p = out_p.with_name(out_p.stem + f"_zoom_{zoom:.2f}".replace(".", "_") + out_p.suffix)
            sz = format_bytes(vid.stat().st_size) if vid.exists() else "0 B"
            table.add_row(str(idx), str(rel), sz, str(out_p.name))

        console.print(table)
        console.print("\n[green]Dry-run complete. No files were modified or encoded.[/green]")
        return 0

    if not args.assume_yes:
        console.print(Panel(
            f"[bold cyan]FLOW VIDEO ZOOM CROP[/bold cyan]\n\nFound [bold]{total}[/bold] video(s) to process.\nTarget Resolution: [bold]{OUT_W}x{OUT_H}[/bold] | Zoom: [bold]{zoom:.2f}x[/bold]\nInput Directory:  [dim]{input_dir}[/dim]\nOutput Directory: [dim]{output_dir}[/dim]\n\n[dim]Responsible Use Notice: Ensure you own or have explicit authorization to crop/modify these media files.[/dim]",
            title="Batch Confirmation",
            border_style="cyan",
        ))
        if not Confirm.ask("Proceed with batch video re-encoding?", default=True):
            console.print("[yellow]Operation cancelled by user. No files were processed.[/yellow]")
            return 0

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

                out_path = output_dir / video.relative_to(input_dir)
                out_path = out_path.with_name(
                    out_path.stem + f"_zoom_{zoom:.2f}".replace(".", "_") + out_path.suffix
                )

                if args.skip_processed and out_path.exists():
                    current_task = make_current_task_card(
                        current_index=i,
                        total=total,
                        rel_path=rel,
                        status="Skipped • Output already exists",
                        recommendation="Output file exists (--skip-processed)",
                        input_size=input_size,
                    )
                    progress.advance(task_id)
                    footer = make_footer(processed, failed)
                    live.update(build_screen(hero, current_task, progress, footer))
                    time.sleep(0.05)
                    continue

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

                    if args.skip_target_res and width == OUT_W and height == OUT_H:
                        current_task = make_current_task_card(
                            current_index=i,
                            total=total,
                            rel_path=rel,
                            status="Skipped • Already target resolution",
                            width=width,
                            height=height,
                            duration=duration,
                            recommendation=f"Already {OUT_W}x{OUT_H} (--skip-target-res)",
                            input_size=input_size,
                        )
                        progress.advance(task_id)
                        footer = make_footer(processed, failed)
                        live.update(build_screen(hero, current_task, progress, footer))
                        time.sleep(0.05)
                        continue

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
