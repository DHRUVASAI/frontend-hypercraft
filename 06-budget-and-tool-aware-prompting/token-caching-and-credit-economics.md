# Token Caching Math, $O(N^2)$ Context Bleed & Credit-Window Strategy

Understanding the exact math of LLM billing explains why two builders using the **same free tier** get wildly different results.

## 1. The $O(N^2)$ Context-Bleed Equation
In any multi-turn builder (Bolt.new, v0, Cursor Agent), every follow-up turn re-sends the entire conversation + active file context $C_0 + t \cdot \Delta C$. Across $N$ uncached turns, cumulative input tokens grow **quadratically**:
$$T_{\text{in}}(N) = \sum_{t=0}^{N-1} (C_0 + t \cdot \Delta C) = N \cdot C_0 + \frac{N(N-1)}{2}\Delta C$$
**Consequence:** Splitting one cleanly specified build into 10 vague back-and-forth turns doesn't cost `2×`—it costs **5× to 8×** more tokens while degrading coherence via context drift.

## 2. Prompt-Cache Economics (Verified `v0 Pro` Calculation)
On `v0 Pro` (`$2.00/1M` uncached input, `$2.50/1M` cache write = `1.25×`, **`$0.10/1M` cache read = `0.05×` — 95% discount!**):
- **Cache Break-Even:** Paying `1.25×` on Turn 1 breaks even after **just 1 cached follow-up turn** (`1.25 + 0.05 = 1.30` vs. `2.00` uncached).
- **Verified 8-Turn Session (`40K` initial context, `4K` output/turn):**
  - Uncached (jumping chats or mutating prefix): **`$1.206`**
  - Prompt-cached (append-only surgical edits within cache TTL): **`$0.534` — saves `55.7%` total bill (and `95%` of repeated input cost)!**
- **Cache-Preservation Rules:**
  1. Never edit or reorder your system instructions / `.cursorrules` mid-session (busts the entire KV prefix cache!).
  2. Batch edits inside the active session window (typically `5–10 min` TTL) rather than sending one message every 20 minutes (every cold wake re-pays `1.25×` cache write!).
  3. Start a **fresh chat** ONLY when switching to an unrelated feature so stale debugging logs stop dragging $C_0$ upward.

## 3. Diff-Scoped Prompting vs. Full-File Rewrites
Output tokens cost **`5×` to `10×` more than input tokens** (`v0 Pro`: `$10/1M` out vs. `$2/1M` in; `v0 Mini`: `$0.50` vs. `$0.10`).
- Asking *"improve the dashboard"* triggers full-file rewrites across 5 files (`~15K` output tokens = `$0.15` on `v0 Pro` or `1.5` Lovable credits).
- Asking *"In `src/components/QuoteBuilder.tsx` ONLY, update lines 42–65 to compute `discount = Math.round(gross * tierPct)`; do not touch other files"* uses `< 1.5K` output tokens — a **10× cost reduction**.

## 4. The "Plan-Outside / Execute-Inside" 2-Run / 2-Day Window Model
Designed specifically for strict daily-reset budgets (e.g., **Lovable Free `5 credits/day`**, **Bolt Free `300K tokens/day`**, **v0 Free `$5` + `7 msg/day`**):

1. **Day 0 (0 Builder Credits — External Free Chat):** Finalize exact copy, WCAG+APCA hex tokens, algebraic formulas, state JSON schema, and `encodeURI()` asset fallbacks outside the metered tool.
2. **Day 1 — Window 1 (Run 1: The Complete Master Shot):** Spend ~50–65% of Day 1 allowance executing the zero-ambiguity 6-Block Master Prompt so Run 1 compiles to **85–95% completeness** with zero placeholders.
3. **Day 1 — Zero-Credit QA Audit:** Inspect desktop, `375px` mobile, browser console, image loads, and every formula. Fix trivial copy/color/year typos manually in **Code View / Design Mode (`0 credits`)**. Log remaining logic/layout defects into ONE numbered list.
4. **Day 1 — Reserve Buffer (Run 1B):** Spend 1 batched surgical prompt ONLY if a blocking defect remains.
5. **Day 2 — Window 2 (After Reset — Run 2: Signature Craft & Final Polish):** Spend Day 2's refreshed allowance on the single batched **Signature Craft Upgrade** (3D PBR polish, optical loupe / Web Audio synth, micro-interactions, SEO metadata) and deploy.
