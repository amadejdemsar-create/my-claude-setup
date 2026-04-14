---
name: remove-watermark
description: "Use when the user asks to remove a watermark, clean a watermark, strip a Gemini watermark, or process images with visible watermarks. Covers single image and batch workflows using the GeminiWatermarkTool CLI."
---

# Remove Watermark (GeminiWatermarkTool)

CLI tool at `/usr/local/bin/GeminiWatermarkTool` (v0.2.5). Removes Gemini visible watermarks from images using reverse alpha blending with optional AI denoising.

## Usage

### Single image (recommended default)
```bash
GeminiWatermarkTool --no-banner -i input.jpg -o clean.jpg --denoise ai
```

### Batch (entire folder)
```bash
GeminiWatermarkTool --no-banner -i ./folder/ -o ./output/ --denoise ai
```

### Quick overwrite (no separate output)
```bash
GeminiWatermarkTool --no-banner input.jpg
```

## Important flags

| Flag | Purpose | Default |
|------|---------|---------|
| `--denoise` | Cleanup method: `ai`, `ns`, `telea`, `soft`, `off` | `off` |
| `--sigma` | AI denoise sigma (1 to 150) | `50` |
| `--strength` | Denoise strength in percent (0 to 300) | `120` for ai, `85` for others |
| `--threshold` | Watermark detection confidence (0.0 to 1.0) | `0.25` |
| `--force` | Skip watermark detection (may damage clean images) | off |
| `--no-banner` | Suppress ASCII art (use this when calling from Claude) | off |
| `-q` / `--quiet` | Suppress all output except errors | off |

## Defaults to apply

- Always use `--no-banner` when calling from Claude Code (cleaner output).
- Default to `--denoise ns` unless the user specifies otherwise. AI denoise (`--denoise ai`) requires Vulkan GPU which is not available on this Mac; `ns` (Navier-Stokes) is the best available fallback.
- When the user provides a single file without specifying output, save the cleaned file next to the original with a `_clean` suffix (e.g., `photo.jpg` becomes `photo_clean.jpg`) rather than overwriting.
- For batch processing, create the output directory if it does not exist before running.

## Output location

Follow the user's instructions for where to save. If no location is specified, save output alongside the input file(s). Never save to `/Users/amadejdemsar/Desktop/` or home directory (per global CLAUDE.md rules, output goes in `/Users/Shared/Domain/` when a project context applies).
