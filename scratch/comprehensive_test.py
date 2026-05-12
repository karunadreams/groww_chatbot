import sys
import json
from src.mf_faq.orchestrator.reasoning import ReasoningEngine

# Force UTF-8 for printing currency symbols
sys.stdout.reconfigure(encoding='utf-8')

def run_comprehensive_test():
    engine = ReasoningEngine()
    
    test_suite = [
        # 1. HDFC Mid Cap
        "What is the current NAV of HDFC Mid Cap Fund?",
        "What is the expense ratio for HDFC Mid Cap?",
        "What is the minimum SIP amount for HDFC Mid Cap?",
        
        # 2. HDFC ELSS (Tax Saver)
        "Tell me about the exit load for HDFC ELSS Tax Saver.",
        "What are the 3-year returns for HDFC ELSS?",
        
        # 3. HDFC Focused 30
        "What is the fund size (AUM) of HDFC Focused 30?",
        "What is the minimum investment for HDFC Focused 30?",
        
        # 4. HDFC Flexi Cap (Equity)
        "What is the NAV of HDFC Flexi Cap Fund?",
        "Is there an exit load for HDFC Flexi Cap?",
        
        # 5. HDFC Top 100 (Large Cap)
        "What is the rating of HDFC Top 100 Fund?",
        "What are the 5-year returns for HDFC Top 100?",
        
        # 6. Comparisons
        "Compare the NAV of HDFC Mid Cap and HDFC Large Cap.",
        "Which has a higher expense ratio: HDFC Mid Cap or HDFC Focused 30?",
        
        # 7. Edge Cases / Guardrails
        "My PAN number is ABCDE1234F, can you help me check my balance?",
        "What is the weather in Mumbai?",
        "Who is the fund manager for HDFC Mid Cap?" # Testing if we capture manager info
    ]
    
    print(f"{'='*60}")
    print(f"HDFC MUTUAL FUND CHATBOT - COMPREHENSIVE AUDIT")
    print(f"{'='*60}\n")
    
    results = []
    
    for query in test_suite:
        print(f"QUERY: {query}")
        try:
            res = engine.generate_answer(query)
            print(f"ANSWER: {res['answer']}")
            print(f"SOURCE: {res['source']}")
            results.append({"query": query, "answer": res['answer'], "source": res['source']})
        except Exception as e:
            print(f"ERROR: {str(e)}")
        print("-" * 40)

    # Save results for review
    with open("scratch/test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_comprehensive_test()
