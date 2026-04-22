# Playbooks Knowledge Library

This directory is the retrieval corpus for JARVIS strategy guidance.

## What JARVIS indexes

- `*.json`
- `*.summary.md`
- `*.summary.txt`

At startup, and whenever `POST /api/knowledge/sync` is called, JARVIS loads those structured files into:

- `knowledge_sources`
- `knowledge_snippets`

## What JARVIS skips

Raw book files such as:

- `.pdf`
- `.epub`
- `.mobi`

Those files are intentionally skipped. The supported workflow is:

1. Start from licensed source material, research, or your own agency notes.
2. Create a structured summary in JSON or `*.summary.md`.
3. Sync the knowledge library.
4. Let JARVIS retrieve the relevant insights during chat, proposal, and candidate evaluation.

## Suggested source shape

Use JSON like this:

```json
{
  "sources": [
    {
      "source_key": "example-source",
      "title": "Example Title",
      "author": "Author Name",
      "source_type": "operator_summary",
      "workflow_stage": "offer_design",
      "tags": ["offers", "pricing"],
      "summary": "One short operator summary.",
      "insights": [
        {
          "content": "A single actionable insight.",
          "workflow_stage": "offer_design",
          "tags": ["offers"],
          "importance": 85
        }
      ]
    }
  ]
}
```
