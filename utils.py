# utils.py
import json
from typing import Dict, List

PROMPT_TEMPLATE = """
You are a friendly, conservative-to-expert Indian financial adviser assistant.
User inputs:
{user_input}

Market data (latest fetched):
{market_context}

Task:
1) Based on the user's capital, monthly investment (SIP), preferred instruments, and risk appetite,
   produce a recommended diversified portfolio in percentages (equities, mutual funds, debt, bonds, cash).
2) For each allocation, suggest 2-4 example instruments available in India (mutual funds by name, sample stocks by ticker, debt/bank options).
3) Provide an estimated projected annualized return for the portfolio over 5 years, with the assumptions used (CAGR calculations based on historical annual returns provided).
4) Provide a short risk explanation and recommended next steps (e.g., start SIP, rebalance after 6 months).
5) If some instruments data is missing, clearly say so.

Format rules (strict):
- Output JSON with fields: allocation (list of {category, percent, instruments}), projected_return (float, percent), assumptions (list), explanation (string).
- Keep output valid JSON (no extra commentary outside the JSON).
"""

def build_prompt(user_input: Dict, market_context: Dict):
    # market_context is dict mapping symbol -> {last, change, timestamp}
    market_str = json.dumps(market_context, indent=2)
    user_str = json.dumps(user_input, indent=2)
    prompt = PROMPT_TEMPLATE.format(user_input=user_str, market_context=market_str)
    return prompt
    