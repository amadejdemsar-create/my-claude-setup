Quick tranche execution check for $ARGUMENTS (format: TICKER, e.g., "AAVE" or "AAVE tranche 2").

This is NOT a full analysis update. This is a fast go/no-go check.

## Steps

1. **Read the existing analysis** at `/Users/Shared/Domain/Context/Personal/finances/crypto/` for the ticker. Find the Execution Rules section (or the tranche table if no Execution Rules section exists yet).

2. **Identify the next open/active tranche.** What is the price zone? What were the conditions?

3. **Get the current price** using CoinMarketCap MCP tools. Get both quotes (price, % changes) and technical analysis (RSI, MACD, Fibonacci, moving averages).

4. **Trend check (mandatory, multi-window).** A single 90d window misclassifies ranges and recoveries as falling knives. Evaluate in this order and pick the FIRST matching label:

   | Condition | Label |
   |---|---|
   | 30d change > 0% AND 7d change > -5% | RECOVERY (even if 90d < -35%, the knife has stopped falling) |
   | Fibonacci swing spread (swingHigh - swingLow) / price < 20% AND price has been inside that range for 30+ days | COMPRESSION / RANGE-BOUND |
   | 30d < -10% AND 7d < -5% AND price making lower lows vs 30d low | FALLING KNIFE (override applies) |
   | 90d between -15% and -35%, price below 200d EMA | DOWNTREND |
   | 90d > -15%, price near or above 200d EMA | UPTREND or CONSOLIDATION |
   | None of the above fit cleanly | MIXED (show the data, do not force a label) |

   **Falling-knife override only fires on the FALLING KNIFE label**, not on any label that includes a -35%+ 90d print. When it fires, a bottoming signal (RSI(14) below 30, volume capitulation spike, double bottom) OR imminent catalyst within 2 weeks is required. Without either, recommend WAIT.

   **COMPRESSION / RANGE-BOUND handling:** a classical bottoming signal will NOT appear in a range (RSI stays 35-55, volume is flat, no waterfall capitulation). Do not wait for one. Evaluate on the analysis's own decision rule. If the range's lower bound aligns with the tranche zone, that IS the setup.

   **RECOVERY handling:** MACD crosses and rising RSI from a bottom count as confirming signals; do not wait for RSI <30 that is already past.

5. **Evaluate the analysis's own decision rule FIRST.** Most analyses define an explicit execute condition in their Execution Rules section (e.g., "2+ technical signals confirm AND price in zone AND no thesis-broken event → EXECUTE"). Check that rule against current data BEFORE applying any trend-based override. Only override if the trend is FALLING KNIFE by the multi-window test above or a THESIS BROKEN event has occurred. Do not stack caution conditions on top of a met decision rule; that is the failure mode this rule exists to prevent.

6. **Classify any material news since the analysis was last updated.** Use the two-bucket classification:
   - **THESIS BROKEN:** exploit, insolvency, regulatory shutdown, fraud, fundamental product failure
   - **RISK ESCALATION:** team changes, governance drama, macro, sentiment, competitors

7. **Output a concise decision table:**

```
TRANCHE CHECK: [TICKER] Tranche [N]
Date: [today]
Analysis last updated: [date]

Price zone: $X-$Y
Current price: $Z [IN ZONE / ABOVE / BELOW]
Trend: [UPTREND / CONSOLIDATION / DOWNTREND / FALLING KNIFE / RECOVERY / COMPRESSION / MIXED]
Fibonacci swing: $low-$high (spread X%, price has held this range for N days)

Multi-window:
- 7d: X%
- 30d: X%
- 90d: X%
- Price vs 200d EMA: X% above/below

Technicals:
- RSI(14): X [CONFIRMS / DOES NOT CONFIRM]
- MACD: [status] [CONFIRMS / DOES NOT CONFIRM]
- Support: [level, holding?]

Analysis's own decision rule: [quote it; state MET / NOT MET]

New developments since last update:
- [event]: RISK ESCALATION (does not override)
- [event]: THESIS BROKEN (overrides) <- only if applicable

RECOMMENDATION: EXECUTE / EXECUTE HALF (state reason) / WAIT (falling knife, no bottoming signal) / WAIT (decision rule not met) / PAUSE (thesis broken)
```

8. If EXECUTE, say so clearly. If WAIT due to falling knife, explain what bottoming signal or catalyst would change the recommendation. If WAIT because the analysis's decision rule is not met, cite which specific signal is missing. If COMPRESSION or RECOVERY and decision rule is met, default to EXECUTE (possibly EXECUTE HALF if one technical is still against, to split risk).

9. **Position sizing.** Do not reference the old DCA plan. Size based on conviction relative to the user's available cash and existing positions. Narrative/speculative plays get smaller sizes than core/high-conviction holds. EXECUTE HALF is allowed when the decision rule is met but one technical remains against the trade, so you participate without full-sizing into resistance.

Do NOT rewrite the full analysis. Do NOT save anything to file. Just output the check.
