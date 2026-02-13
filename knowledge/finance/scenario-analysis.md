# Scenario Analysis & Sentiment Framework

Shared framework for consistent bear/base/bull scenario analysis across stock and crypto research.

## Scenario Table Format

Every analysis MUST include a scenario summary table with timelines:

| Scenario | Probability | Market Cap | Price | Multiple | Timeline |
|----------|------------|------------|-------|----------|----------|
| Bear | X% | $X | $X | X.Xx | X-X months |
| Base | X% | $X | $X | X.Xx | X-X months |
| Bull | X% | $X | $X | X.Xx | X-X months |

**Expected Value (probability-weighted):** Always calculate and state.

## Timeline Guidelines

Timelines represent when the scenario would likely materialize, not when it "ends."

### Bear Case Timelines
Bear scenarios tend to play out faster than bull scenarios (markets take stairs up, elevator down).

| Asset Type | Typical Bear Timeline | Driver |
|------------|----------------------|--------|
| Large-cap stocks | 3-12 months | Earnings misses compound over 2-3 quarters |
| Small/mid-cap stocks | 2-9 months | Liquidity dries up faster, sharper moves |
| Crypto (large cap) | 2-6 months | High volatility, sentiment shifts fast |
| Crypto (mid/small cap) | 1-6 months | Can collapse within weeks on narrative death |

### Base Case Timelines
Base case = thesis plays out at moderate pace. Driven by fundamentals catching up to valuation.

| Asset Type | Typical Base Timeline | Driver |
|------------|----------------------|--------|
| Large-cap stocks | 12-24 months | Multiple re-rating + earnings growth |
| Small/mid-cap stocks | 12-18 months | Growth recognition, analyst coverage |
| Crypto (large cap) | 12-24 months | Cycle recovery + adoption milestones |
| Crypto (mid/small cap) | 6-18 months | Narrative rotation + usage growth |

### Bull Case Timelines
Bull cases need multiple catalysts to align. Usually takes longer.

| Asset Type | Typical Bull Timeline | Driver |
|------------|----------------------|--------|
| Large-cap stocks | 18-36 months | Sustained beat-and-raise + sector tailwind |
| Small/mid-cap stocks | 12-30 months | Breakout growth + market discovery |
| Crypto (large cap) | 18-36 months | Full cycle bull + ecosystem dominance |
| Crypto (mid/small cap) | 12-36 months | Narrative peak + real adoption inflection |

## Sentiment Analysis Checklist

Run this checklist for every analysis to ensure consistent sentiment assessment.

### Market-Wide Sentiment
- [ ] **Fear & Greed Index**: Current reading and 30-day trend
- [ ] **VIX / Crypto Vol**: Elevated (>25 VIX) or calm (<15 VIX)?
- [ ] **Funding rates** (crypto): Positive (overleveraged longs) or negative (capitulation)?
- [ ] **Put/Call ratio** (stocks): >1.0 (bearish) or <0.7 (complacent)?
- [ ] **Analyst consensus**: Overwhelmingly bullish (contrarian sell) or bearish (contrarian buy)?

### Asset-Specific Sentiment
- [ ] **Distance from ATH/ATL**: How much pain have holders endured?
- [ ] **Short interest** (stocks) / **Funding rate** (crypto): Crowded shorts = squeeze potential
- [ ] **Social sentiment**: Trending topic (late) or forgotten (early)?
- [ ] **Insider activity**: Buying (bullish signal) or selling (could be routine)?
- [ ] **Institutional flows**: Accumulation or distribution phase?

### Cycle Positioning
- [ ] **Where in the macro cycle**: Early recovery / expansion / late cycle / contraction?
- [ ] **Where in the sector cycle**: Emerging narrative / growth / maturity / decline?
- [ ] **BTC halving cycle** (crypto only): Pre-halving / post-halving year 1 / year 2 / year 3?

### Sentiment Score

Synthesize into a single score:

| Score | Label | Meaning |
|-------|-------|---------|
| 1-2 | Extreme Fear | Historically excellent buying zone if fundamentals intact |
| 3-4 | Fear | Good risk/reward for quality assets |
| 5-6 | Neutral | Normal conditions, fundamentals-driven |
| 7-8 | Greed | Reduce exposure, tighten stops |
| 9-10 | Extreme Greed | High probability of correction. Take profits |

## Scenario Construction Rules

1. **Probabilities must sum to 100%** (or close -- a small "black swan" residual is OK)
2. **Bear case is never <15% probability** -- things can always go wrong
3. **Bull case is never >35% probability** -- don't be a moonboy
4. **Each scenario needs specific triggers** -- not just "things go bad" or "things go well"
5. **Market cap sanity check**: Compare bull case market cap to established peers. If your bull case makes a $500M project worth more than the sector leader, your assumptions are wrong
6. **Timeline must be stated** for every scenario -- vague "eventually" is not a thesis
7. **Expected value must be positive** for the recommendation to be "buy" -- if probability-weighted outcome is negative, it's a pass regardless of bull case upside

## Connecting Sentiment to Scenarios

Sentiment directly affects scenario probabilities:

| Current Sentiment | Bear Prob Adjustment | Bull Prob Adjustment |
|-------------------|---------------------|---------------------|
| Extreme Fear (1-2) | -5% (less likely, already priced in) | +5% (mean reversion) |
| Fear (3-4) | -3% | +3% |
| Neutral (5-6) | No adjustment | No adjustment |
| Greed (7-8) | +3% | -3% |
| Extreme Greed (9-10) | +5% (correction overdue) | -5% (upside priced in) |

This is a starting heuristic, not a rigid rule. Override with fundamental conviction when warranted.

## Used By
- `~/.claude/agents/stock-analyst.md`
- `~/.claude/agents/crypto-analyst.md`
