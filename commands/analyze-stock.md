Use the stock-analyst agent to perform a full deep-dive equity research analysis on $ARGUMENTS.

Read the knowledge base files at `~/.claude/knowledge/finance/` before starting. These contain the analytical frameworks (fundamentals, technicals, macro, geopolitics, psychology, risk management, stock valuation, news interpretation, scenario analysis) that power the analysis.

Follow the complete 8-step analysis framework:
1. Data Gathering (pull financials, news, price data)
2. Fundamental Deep Dive (revenue, margins, cash flow, moat)
3. Valuation (relative + intrinsic, sector-specific model)
4. Technical Picture (trend, support/resistance, momentum)
5. Macro & Geopolitical Context
6. Sentiment & Psychology Check
7. Scenario Analysis (bear/base/bull with price targets)
8. Final Verdict (score, action, risk level)

Save the result to `~/analyses/stocks/[ticker-lowercase].md`

If an analysis already exists for this ticker, update it rather than overwriting.
