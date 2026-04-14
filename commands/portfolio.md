Load my complete portfolio context and prepare for a financial discussion.

## Step 1: Read Portfolio State

Read these files:
1. `/Users/Shared/Domain/Context/Personal/finances/portfolio.md` (active positions, entries, stop losses, targets, cash)
2. `/Users/Shared/Domain/Context/Personal/0x100x-watchlist.json` (price conditions being monitored)
3. `/Users/Shared/Domain/Context/Personal/finances/crypto/index.md` (research scores and analysis)

## Step 2: Check Automation Logs

Read the last 50 lines of `~/.claude/scripts/0x100x-check.log` to see recent automation results and alerts.

## Step 3: Get Live Prices

For every active position in portfolio.md, use CoinMarketCap MCP tools:
1. `mcp__coinmarketcap__search_cryptos` to find coin IDs
2. `mcp__coinmarketcap__get_crypto_quotes_latest` to get current prices, 24h change, 7d change
3. Calculate current P&L for each position (current price vs entry price, accounting for leverage)

## Step 4: Check Watchlist Against Live Prices

For each "watching" entry in the watchlist JSON:
- Get the current price
- Check if the condition has been met
- Flag any triggered or nearly triggered conditions (within 2% of trigger price)

## Step 5: Present Summary

Format a concise portfolio dashboard:

**POSITIONS** (table: asset, entry, current, P&L %, leverage, distance to SL, distance to TP)

**WATCHLIST ALERTS** (any triggered or near-trigger conditions)

**CASH AVAILABLE** (from portfolio.md)

**RECENT 0x100x ACTIVITY** (key points from automation log)

**PORTFOLIO HEALTH** (overall risk assessment: stop loss proximity, leverage, concentration risk)

Then ask: "What would you like to discuss? Positions, watchlist, new trades, or risk review?"
