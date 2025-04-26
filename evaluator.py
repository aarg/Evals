import os
from openai import OpenAI
from dotenv import load_dotenv
import textstat

EVAL_PROMPT = """
You are an expert content editor specializing in digital content optimization.
Evaluate the blog post provided below thoroughly across these key parameters. You are only evaluating the text content — do not expect or assess any visual elements such as images, charts, or layout styling. For each parameter, assign a score from 0.0 (unacceptable) to 5.0 (exceptional). Provide short justification **supported by specific examples or direct references from the text where possible**.

**Evaluation Parameters:**

1.  **Tone of Voice:** Assess consistency, appropriateness, emotional resonance, and authenticity.
2.  **Style:** Evaluate writing quality, clarity, vocabulary, sentence variety, and engagement.
3.  **Structure & Readability:** Analyze headline, organization, transitions, subheadings, conclusion, formatting for clarity, and overall readability.
4.  **Format:** Examine text formatting consistency.
5.  **Flow:** Evaluate logical sequence, transitions, pacing, and reader engagement from start to finish.

**Scoring Guide:**
* 0.0 - 1.0: Unacceptable / Major flaws hindering purpose.
* 1.1 - 2.0: Poor / Needs significant revision.
* 2.1 - 3.0: Fair / Several areas need improvement.
* 3.1 - 4.0: Good / Generally effective, minor tweaks possible.
* 4.1 - 4.9: Very Good / High quality, meets objectives well.
* 5.0: Exceptional / Outstanding, near-perfect execution.

**Respond strictly in the following JSON format:**
```json
{
  "Tone of Voice": {"score": <float_score_0.0_to_5.0>, "reason": "<short_justification_with_specific_examples>"},
  "Style": {"score": <float_score_0.0_to_5.0>, "reason": "<short_justification_with_specific_examples>"},
  "Structure & Readability": {"score": <float_score_0.0_to_5.0>, "reason": "<short_justification_with_specific_examples>"},
  "Format": {"score": <float_score_0.0_to_5.0>, "reason": "<short_justification_with_specific_examples>"},
  "Flow": {"score": <float_score_0.0_to_5.0>, "reason": "<short_justification_with_specific_examples>"}
}
```

**IMPORTANT INSTRUCTION FOR PROCESSING INPUT:**
The text provided below might contain extra content from a web page (like navigation links, headers, footers, ads, related posts, or comments). **Identify and focus *only* on the main blog post article content (headline, author info if present, body paragraphs, subheadings).** Ignore all other extraneous text. Your evaluation scores and reasons must be based *solely* on this core article content.

**Blog post to evaluate:**
"""

import os
from openai import OpenAI
from google import genai
from dotenv import load_dotenv
import textstat
import requests

load_dotenv()

def robust_json_parse(text):
    import re, json
    # Remove Markdown code block if present
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text)
    # Try strict parse first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to extract JSON substring
    match = re.search(r'\{[\s\S]+\}', text)
    if match:
        candidate = match.group(0)
        # Remove trailing commas
        candidate = re.sub(r',([ \t\r\n]*[}\]])', r'\1', candidate)
        # Replace single quotes with double quotes
        candidate = candidate.replace("'", '"')
        try:
            return json.loads(candidate)
        except Exception as e:
            print("Still failed to parse JSON:", e)
            print("Candidate JSON:", candidate)
            raise
    print("Could not extract JSON from:", text)
    raise ValueError("Invalid JSON")

def evaluate_article(text: str, model: str) -> dict:
    import json, re
    load_dotenv()
    prompt = EVAL_PROMPT + text
    if model == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.0,
        )
        content = response.choices[0].message.content
    elif model == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        content = resp.json()["content"][0]["text"]
    elif model == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        content = response.text
    else:
        raise ValueError(f"Unknown model: {model}")
    #print(f"\n[DEBUG] Raw LLM output for model {model}:\n{content}\n")
    try:
        return robust_json_parse(content)
    except Exception:
        raise ValueError(f"Could not parse LLM response as JSON for model {model}")

def flesch_kincaid_score(text: str) -> float:
    return textstat.flesch_kincaid_grade(text)