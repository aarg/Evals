import sys
from datetime import datetime
from fetcher import fetch_article_content, save_article
from evaluator import evaluate_article, flesch_kincaid_score
import csv

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <article_url1>[,article_url2,...] <model>")
        print("Model options: openai, claude, gemini, all")
        sys.exit(1)
    urls = [u.strip() for u in sys.argv[1].split(',') if u.strip()]
    model_arg = sys.argv[2].lower()
    if model_arg == "all":
        models = ["openai", "claude", "gemini"]
    elif model_arg in ("openai", "claude", "gemini"):
        models = [model_arg]
    else:
        print("Invalid model. Choose from: openai, claude, gemini, all")
        sys.exit(1)
    results = []
    for url in urls:
        print(f"Fetching article from: {url}")
        text = fetch_article_content(url)
        if not text or len(text.strip()) < 100:
            print(f"Failed to extract sufficient article content from {url}.")
            continue
        filename = save_article(text, url)
        print(f"\nArticle saved to {filename}")
        print("\n================== BLOG ARTICLE EVALUATION ==================")
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Date: {now}")
        print(f"Source URL: {url}")
        print(f"Saved as: {filename}")
        print("============================================================\n")
        for model in models:
            print(f"Evaluating with {model}...")
            try:
                eval_result = evaluate_article(text, model)
            except Exception as e:
                print(f"Error evaluating with {model}: {e}")
                continue
            # Section: Scores & Reasoning
            print(f"------------------ SCORES & REASONING ({model.upper()}) ------------------")
            for param, details in eval_result.items():
                if isinstance(details, dict) and 'score' in details:
                    print(f"\n{param.upper()}:")
                    print(f"  Score   : {details['score']}/5")
                    print(f"  Reason  : {details['reason']}")
            print("---------------------------------------------------------\n")
            fk_score = flesch_kincaid_score(text)
            print(f"------------------ READABILITY ({model.upper()}) ------------------")
            print(f"Flesch-Kincaid Grade Level: {fk_score:.2f}")
            print("-------------------------------------------------")
            # Prepare data for CSV
            results.append({
                'date': now,
                'url': url,
                'filename': filename,
                'model': model,
                'tone_of_voice_score': eval_result['Tone of Voice']['score'],
                'tone_of_voice_reason': eval_result['Tone of Voice']['reason'],
                'style_score': eval_result['Style']['score'],
                'style_reason': eval_result['Style']['reason'],
                'structure_readability_score': eval_result['Structure & Readability']['score'],
                'structure_readability_reason': eval_result['Structure & Readability']['reason'],
                'format_score': eval_result['Format']['score'],
                'format_reason': eval_result['Format']['reason'],
                'flow_score': eval_result['Flow']['score'],
                'flow_reason': eval_result['Flow']['reason'],
                'flesch_kincaid_grade': fk_score,
            })
    # Write HTML to a subdirectory
    html_dir = "eval_results_html"
    import os
    os.makedirs(html_dir, exist_ok=True)
    html_file = os.path.join(html_dir, f"eval_results_graphs_{now.replace(':', '-').replace(' ', '_')}.html")
    import json
    html_results_json = json.dumps(results, indent=2)
    # Read HTML template from external file
    with open("eval_results_template.html", "r", encoding="utf-8") as tpl_file:
        html_template = tpl_file.read()
    html_template = html_template.replace('__HTML_RESULTS_JSON__', html_results_json)

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"\nHTML visualization written to {html_file}")
    # Write/appends results to CSV
    if results:
        csv_file = 'eval_results.csv'
        fieldnames = [
            'date','url','filename','model','tone_of_voice_score','tone_of_voice_reason',
            'style_score','style_reason','structure_readability_score','structure_readability_reason',
            'format_score','format_reason','flow_score','flow_reason','flesch_kincaid_grade']
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                has_header = f.readline().strip().startswith('date')
        except FileNotFoundError:
            has_header = False
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not has_header:
                writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"\nResults appended to {csv_file}")

if __name__ == "__main__":
    main()
