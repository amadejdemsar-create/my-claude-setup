# /visualize <source>

Transform any text source (book, article, essay, notes) into a premium visual HTML page that explains the key principles, frameworks, and ideas. Optionally personalized to the reader based on available context.

## Arguments

- `<source>`: Path to the source file (required). Accepts `.md`, `.txt`, `.pdf`, or any text format. Can also be a URL to scrape.

## Step 1: Ingest the Source and Ensure a Markdown Version Exists

The working format is always `.md`. Every source must be converted to markdown first, saved alongside the original, and then used as the source of truth for HTML generation.

### Check if a markdown version already exists

Before doing any conversion, check if a `.md` file with the same base name already exists in the same directory (e.g., for `my-book.pdf`, check for `my-book.md`). If it exists, use it directly and skip conversion.

### Conversion by format

- **`.md`**: Already in working format. Use directly.
- **`.txt`**: Rename/copy to `.md` or treat as markdown directly (text files are already plain text).
- **`.pdf`**: Read the full PDF using the Read tool with `pages` parameter (20 pages at a time for large files). Convert the extracted content into well-structured markdown: add headings for chapters/sections, preserve paragraph breaks, format lists, and clean up any extraction artifacts (broken words, stray page numbers, headers/footers). Save the resulting markdown as `<source-name>.md` in the same directory as the PDF.
- **URL**: Use web scraping tools to fetch the page content. Save the scraped markdown as `<topic-name>.md` in an appropriate directory.
- **Other formats** (`.epub`, `.docx`, `.rtf`, etc.): Attempt to read with the Read tool. If the content is intelligible, convert it to clean markdown and save as `<source-name>.md` alongside the original. If the content is garbled or unreadable, inform the user and ask them to provide a `.md` or `.pdf` version instead.

### After conversion

Confirm to the user: the title, approximate length, topic, and the path where the `.md` file was saved. From this point forward, all content extraction works from the `.md` file, never from the original format.

## Step 2: Ask the User Two Questions

Before generating anything, ask:

**Question 1: Mode**
> "Would you like me to:
> (A) Just explain the key principles and frameworks from this source, or
> (B) Personalize it: explain the principles AND apply them specifically to you based on your context?"

**Question 2: Depth**
> "How deep should this go?
> (A) Executive summary: the 3 to 5 biggest ideas, compact (single page feel)
> (B) Comprehensive: all major concepts, frameworks, and principles covered in full sections
> (C) Deep dive: everything above plus detailed breakdowns, diagrams, and supporting arguments"

Wait for the user's answers before proceeding.

## Step 3: Extract the Core Content

Read the full source carefully and identify:

- **The central thesis / big idea**: What is the ONE thing this source is really about?
- **Key frameworks**: Any named models, diagrams, processes, or systems
- **Core principles**: The major ideas, usually 3 to 10 depending on source length
- **Memorable quotes**: 2 to 4 powerful quotes that capture the essence
- **Actionable techniques**: Specific practices, exercises, or methods the author recommends
- **Contrasts and tensions**: What the source argues against (old way vs new way, common mistake vs correct approach)

Write these down as structured notes before moving to HTML generation.

## Step 4: If Personalized Mode, Read Context

If the user chose personalized (B), look for personal context files that describe the reader's situation. Common locations include a `me/` or `personal/` directory with files like `about.md`, `experience.md`, `skills.md`, `preferences.md`, or a plans directory with goals and current priorities.

Use this context to:
- Apply each principle specifically to the reader's situation
- Create "YOU:" annotations that connect book concepts to their real life
- Design personalized exercises and action items
- Identify which principles are most relevant to their current challenges
- Map frameworks to their actual goals, businesses, habits, and circumstances

If no context files exist, ask the user to briefly describe their situation, goals, and current challenges so you can personalize effectively.

## Step 5: Generate the HTML

Create a single, self-contained HTML file. No external dependencies except Google Fonts. The design language must match this established visual system:

### Design System

**Typography:**
- Import: `Inter` (300, 400, 500, 600, 700, 800, 900) and `Playfair Display` (700, 700 italic)
- Body: Inter. Headlines and hero: Playfair Display.
- Hero title: `clamp(44px, 6.5vw, 88px)`
- Section titles: `clamp(32px, 4vw, 48px)`
- Body text: 15 to 17px. Dim text: 13 to 14px.
- Labels: 11 to 13px, uppercase, letter-spacing 2 to 3px, font-weight 700

**Color System (CSS custom properties in `:root`):**
- Background: very dark (near-black with a subtle hue, e.g. `#06060c`, `#0a0a0f`)
- Cards: slightly lighter dark (`#0e0e18`, `#111118`)
- Card hover: one step lighter (`#141420`, `#16161f`)
- Border: subtle (`#1a1a2e`, `#1e1e2a`)
- Text: light (`#e4e4f0`, `#e8e8f0`)
- Text dim: muted (`#7a7a96`, `#8888a0`)
- Accent: ONE primary accent color chosen to match the source's theme/mood
  - Warm gold/amber for self-improvement, psychology, mindset books
  - Purple for creativity, philosophy, spirituality
  - Teal/cyan for science, technology, systems thinking
  - Blue for business, strategy, leadership
  - Green for health, nature, sustainability
  - Orange for energy, entrepreneurship, action
- Accent glow: the accent at 8 to 15% opacity for subtle backgrounds
- Semantic colors: always include green (positive), red (negative/warning), and 2 to 3 supporting colors with their glow variants

**Layout:**
- Container: `max-width: 1100px; margin: 0 auto; padding: 0 24px;`
- Sections: `padding: 100px 0;`
- Dividers between sections: `linear-gradient(90deg, transparent, var(--border), transparent)`

**Cards:**
- Background: `var(--card)`, border: `1px solid var(--border)`, border-radius: 14 to 20px
- Hover: `translateY(-2px)` and border-color change, `transition: all 0.3s ease`
- Big idea cards: larger padding (48px), subtle radial gradient glow in corner

**Tags/Pills:**
- Inline-block, 11px uppercase, letter-spacing 2px
- Background: semantic color at 8 to 12% opacity, text in the semantic color
- Padding: `4px 12px`, border-radius: 6px

**Structure (top to bottom):**

1. **Hero section**: full viewport height, centered. Label (uppercase small text), giant title (Playfair, gradient text), subtitle paragraph, meta line (author/date/category)
2. **Core Mechanism / Big Idea**: the central thesis explained with a big-idea card and optional diagram
3. **Key Principles / Frameworks**: each principle gets its own section or card grid. Use varied layouts:
   - 2-column card grids for comparisons (e.g. "old way vs new way", "success vs failure")
   - Vertical timelines for sequential processes
   - 3-column grids for collections of techniques/habits
   - Single large cards for big ideas that need space
4. **Diagrams**: for any process or system, create CSS-only diagrams (grids with arrows, node layouts, flow charts). No images needed.
5. **Quotes**: centered, Playfair italic, larger font, with cite element
6. **If personalized**: "Applied to You" sections interspersed throughout, with `YOU:` markers in accent color, personal action items, and specific techniques tied to the reader's situation
7. **Prescriptions / Action Items**: numbered cards with priority markers. If personalized, these are specific to the reader. If principles-only, these are the author's recommended practices.
8. **Closing section**: shorter hero-style section with gradient text headline and a single compelling closing paragraph

**Responsive Design (mandatory):**

Include a `@media (max-width: 768px)` block that:
- Collapses all grids to single column
- Reduces padding and font sizes proportionally
- Removes hover transforms (mobile has no hover)
- Stacks horizontal diagrams vertically with rotated arrows
- Adjusts hero to `min-height: auto`

Include a `@media (max-width: 380px)` block for small phones with further size reductions.

### Content Guidelines

- Write in clear, direct language. No filler, no fluff.
- Each section should stand alone as a useful explanation of that concept.
- Use the book's own terminology and frameworks, not generic self-help language.
- If the source has a specific structure (numbered principles, acronyms, chapters), honor that structure in the visual layout.
- Quotes should be the source's actual words, properly attributed.
- If personalized, the "YOU:" sections should be honest, specific, and actionable. Reference real details from the person's life, not vague encouragements.

## Step 6: Save the File

Save the HTML file in the same directory as the source file, named: `<source-name>-applied.html` (if personalized) or `<source-name>-visual.html` (if principles only).

Tell the user the file path and offer to open it in the browser with `open <path>`.

## Key Rules

- Never start generating HTML before getting the user's mode and depth answers
- The HTML must be a single self-contained file (inline CSS, no external stylesheets beyond Google Fonts)
- Every section needs both desktop and mobile styling
- Color scheme should feel intentional and themed to the source material
- If personalized, read the actual context files; do not guess or fabricate personal details
- Quotes must be real quotes from the source, never fabricated
