# Blog Post Evaluator

`blog_evaluator` is a Python application that automatically fetches, analyzes, and scores blog articles using Large Language Models (LLMs) such as OpenAI GPT, Claude, and Gemini. It provides both quantitative and qualitative feedback on blog content, with a focus on writing quality, clarity, and structure.

## What does `blog_evaluator` do?
- **Fetches Blog Articles:** Given one or more URLs, the tool downloads and extracts the main textual content of each blog post.
- **Evaluates Content Using LLMs:** For each article, the tool prompts an LLM to score and justify the article across five key parameters:
  1. Tone of Voice
  2. Style
  3. Structure & Readability
  4. Format (text formatting consistency)
  5. Flow
- **Provides Readability Metrics:** Calculates the Flesch-Kincaid readability grade for each article.
- **Saves and Visualizes Results:**
  - Raw article text is saved in the `articles/` directory.
  - Evaluation results are saved in CSV and JSON formats for further analysis.
  - Interactive HTML visualizations (with line graphs and hoverable justifications) are generated in the `eval_results_html/` directory.
- **Console Output:** Prints detailed scores and LLM justifications for each parameter directly to the terminal for immediate feedback.

## Output
- Blog post text files in `articles/`
- Evaluation results in CSV and JSON formats
- Interactive HTML visualizations in `eval_results_html/`
- Readability scores and parameter breakdowns printed to the console

## Example Use Cases
- Benchmarking writing quality across multiple blogs or authors
- Tracking improvements to a blog over time
- Comparing LLM model performance on content evaluation tasks
- Quickly identifying strengths and weaknesses in article drafts

## Requirements
- Python 3.8+
- API keys for OpenAI, Anthropic (Claude), and/or Google Gemini (set in `.env`)
- See `requirements.txt` for dependencies

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your API keys in a `.env` file:
   ```env
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   GOOGLE_API_KEY=your-google-key
   ```
3. Run the evaluator:
   ```bash
   python main.py <article_url1>,<article_url2> ...<modelname (openai|claude|gemini|all)>
   ```
4. View results in the console, CSV/JSON files, and open the generated HTML visualizations in `eval_results_html/`.

## License
MIT
