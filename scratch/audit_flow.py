import sys
from src.mf_faq.orchestrator.reasoning import ReasoningEngine

# Force UTF-8 for printing
sys.stdout.reconfigure(encoding='utf-8')

engine = ReasoningEngine()
query = "What is the NAV and Expense Ratio of HDFC Mid Cap?"
result = engine.generate_answer(query)

print(f"--- TEST AUDIT ---")
print(f"Query: {query}")
print(f"Answer: {result['answer']}")
print(f"Source: {result['source']}")
print(f"------------------")
