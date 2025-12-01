"""
Interactive NiraCare Runner

Run this to test NiraCare with your own symptom descriptions.
You can type or paste your symptoms, answer follow-up questions, and see the results.
"""

import os
import warnings
import sys

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Fix importlib.metadata issue
try:
    import importlib.metadata
    if not hasattr(importlib.metadata, 'packages_distributions'):
        # Patch for older Python versions
        import importlib_metadata
        importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
except:
    pass

from niracare_pipeline import NiraSession, run_niracare_with_user_answers
from niracare_agents import (
    run_intake_agent,
    run_clarifier_agent,
    run_summary_agent,
    run_routing_agent,
    run_eval_agent
)

# Check if API key is set
if not os.getenv("GOOGLE_API_KEY"):
    print("=" * 80)
    print("ERROR: GOOGLE_API_KEY not found!")
    print("=" * 80)
    print("\nPlease set your API key in the .env file or as an environment variable.")
    exit(1)

print("=" * 80)
print("NIRACARE - Interactive Test")
print("=" * 80)
print("\nEnter your symptom description below.")
print("You can type multiple lines. When done, press Enter on an empty line.")
print("Or type 'quit' to exit.\n")
print("-" * 80)

while True:
    print("\n📝 Enter your symptoms (or 'quit' to exit):")
    print("(Press Enter on empty line when done, or type 'quit')")
    
    lines = []
    while True:
        line = input()
        if line.strip().lower() == 'quit':
            print("\n👋 Goodbye!")
            exit(0)
        if line.strip() == '':
            break
        lines.append(line)
    
    if not lines:
        print("⚠️  No input provided. Try again.")
        continue
    
    symptom_text = "\n".join(lines)
    
    print("\n" + "=" * 80)
    print("STEP 1: EXTRACTING SYMPTOMS...")
    print("=" * 80)
    
    try:
        # Step 1: IntakeAgent
        intake_json = run_intake_agent(symptom_text)
        print("\n✅ Symptoms extracted!")
        print(f"   Found {len(intake_json.get('symptoms', []))} symptom(s)")
        
        # Step 2: ClarifierAgent
        print("\n" + "=" * 80)
        print("STEP 2: GENERATING FOLLOW-UP QUESTIONS...")
        print("=" * 80)
        
        clarifier_output = run_clarifier_agent(symptom_text, intake_json)
        clarifier_questions = clarifier_output.get("questions", [])
        
        if not clarifier_questions:
            print("\n✅ No follow-up questions needed!")
            clarifier_answers = {}
        else:
            print(f"\n✅ Generated {len(clarifier_questions)} follow-up question(s):\n")
            
            # Step 3: Get user answers
            print("=" * 80)
            print("STEP 3: ANSWER THE FOLLOW-UP QUESTIONS")
            print("=" * 80)
            print("\nPlease answer each question. Press Enter after each answer.\n")
            
            clarifier_answers = {}
            for i, question in enumerate(clarifier_questions, 1):
                print(f"\n❓ Question {i}/{len(clarifier_questions)}:")
                print(f"   {question}")
                answer = input("   Your answer: ").strip()
                if answer:
                    clarifier_answers[question] = answer
                else:
                    clarifier_answers[question] = "(No answer provided)"
        
        # Step 4: SummaryAgent
        print("\n" + "=" * 80)
        print("STEP 4: CREATING DOCTOR NOTE...")
        print("=" * 80)
        
        doctor_note = run_summary_agent(symptom_text, intake_json, clarifier_answers)
        
        print("\n" + "=" * 80)
        print("DOCTOR NOTE:")
        print("=" * 80)
        print(doctor_note)
        
        # Step 5: RoutingAgent
        print("\n" + "=" * 80)
        print("STEP 5: ROUTING GUIDANCE (DOCTOR & TEST SUGGESTIONS)...")
        print("=" * 80)
        
        routing_guidance = run_routing_agent(symptom_text, intake_json)
        
        doctors = routing_guidance.get("recommended_doctors", [])
        if doctors:
            print("\n👨‍⚕️ Recommended Doctor Types:")
            for i, doc in enumerate(doctors, 1):
                print(f"\n   {i}. {doc.get('type', 'Unknown')}")
                if doc.get('reason'):
                    print(f"      Reason: {doc['reason']}")
        
        tests = routing_guidance.get("possible_test_categories", [])
        if tests:
            print("\n🔬 Possible Test Categories:")
            for i, test in enumerate(tests, 1):
                print(f"\n   {i}. {test.get('category', 'Unknown')}")
                if test.get('purpose'):
                    print(f"      Purpose: {test['purpose']}")
        
        urgency = routing_guidance.get("urgency_note", "")
        if urgency:
            print(f"\n⚠️  {urgency}")
        
        # Step 6: EvalAgent
        print("\n" + "=" * 80)
        print("STEP 6: EVALUATING NOTE QUALITY...")
        print("=" * 80)
        
        eval_result = run_eval_agent(doctor_note)
        
        print("\n" + "=" * 80)
        print("EVALUATION RESULTS:")
        print("=" * 80)
        print(f"\n📊 Quality Score: {eval_result.get('score', 'N/A')}/10")
        
        missing_fields = eval_result.get('missing_fields', [])
        if missing_fields:
            print(f"\n⚠️  Missing Fields:")
            for field in missing_fields:
                print(f"   • {field}")
        
        improvement = eval_result.get('suggested_improvement', '')
        if improvement:
            print(f"\n💡 Suggested Improvement:")
            print(f"   {improvement}")
        
        print("\n" + "=" * 80)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Final Summary:")
        print(f"   • Symptoms extracted: {len(intake_json.get('symptoms', []))}")
        print(f"   • Questions answered: {len(clarifier_answers)}")
        print(f"   • Doctor types suggested: {len(doctors)}")
        print(f"   • Note quality score: {eval_result.get('score', 'N/A')}/10")
        
        print("\n" + "=" * 80)
        print("Would you like to run another test? (y/n)")
        choice = input().strip().lower()
        if choice != 'y':
            print("\n👋 Thanks for testing NiraCare!")
            break
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\nWould you like to try again? (y/n)")
        choice = input().strip().lower()
        if choice != 'y':
            break

