"""
NiraCare Pipeline Module

Orchestrates the multi-agent workflow:
1. IntakeAgent extracts structured symptoms
2. ClarifierAgent generates follow-up questions
3. (Auto-answered for demo purposes)
4. SummaryAgent creates doctor-ready visit note
5. EvalAgent evaluates note quality

This module demonstrates:
- Multi-agent orchestration (4 agents working together)
- Session state management (NiraSession dataclass)
- End-to-end pipeline execution
"""

import warnings
import os
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Fix importlib.metadata issue
try:
    import importlib.metadata
    if not hasattr(importlib.metadata, 'packages_distributions'):
        try:
            import importlib_metadata
            importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
        except ImportError:
            pass
except:
    pass

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

from niracare_agents import (
    run_intake_agent,
    run_clarifier_agent,
    run_summary_agent,
    run_routing_agent,
    run_eval_agent
)


@dataclass
class NiraSession:
    """
    Session state container for NiraCare pipeline.
    
    This dataclass holds all intermediate and final outputs from the
    multi-agent workflow, demonstrating session state management.
    """
    raw_text: str = ""
    intake_json: Dict = field(default_factory=dict)
    clarifier_questions: List[str] = field(default_factory=list)
    clarifier_answers: Dict[str, str] = field(default_factory=dict)
    doctor_note: str = ""
    routing_guidance: Dict = field(default_factory=dict)
    eval_result: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary for easy inspection."""
        return {
            "raw_text": self.raw_text,
            "intake_json": self.intake_json,
            "clarifier_questions": self.clarifier_questions,
            "clarifier_answers": self.clarifier_answers,
            "doctor_note": self.doctor_note,
            "routing_guidance": self.routing_guidance,
            "eval_result": self.eval_result
        }


def auto_answer_clarifier_questions(questions: List[str]) -> Dict[str, str]:
    """
    Auto-answers clarifier questions with dummy responses for demo purposes.
    
    In a production system, these would be answered by the user.
    For the demo pipeline, we generate placeholder answers so the
    workflow can run end-to-end without human intervention.
    
    Args:
        questions: List of questions from ClarifierAgent
        
    Returns:
        Dictionary mapping each question to a demo answer
    """
    answers = {}
    for question in questions:
        # Generate a simple demo answer
        answers[question] = f"Demo answer for: {question}"
    return answers


def run_niracare_demo(raw_text: str) -> NiraSession:
    """
    Orchestrates the complete NiraCare multi-agent pipeline.
    
    This function demonstrates multi-agent orchestration by:
    1. Running IntakeAgent to extract structured symptoms
    2. Running ClarifierAgent to generate follow-up questions
    3. Auto-answering questions (for demo purposes)
    4. Running SummaryAgent to create doctor-ready visit note
    5. Running EvalAgent to evaluate note quality
    
    Each step is printed with clear labels so judges can see
    the progression through the multi-agent system.
    
    Args:
        raw_text: Raw free-text description from user
        
    Returns:
        NiraSession object containing all intermediate and final outputs
    """
    session = NiraSession(raw_text=raw_text)
    
    print("=" * 80)
    print("NIRACARE MULTI-AGENT PIPELINE")
    print("=" * 80)
    print()
    
    # ========================================================================
    # Step 1: IntakeAgent - Extract structured symptoms
    # ========================================================================
    print("STEP 1: INTAKE AGENT")
    print("-" * 80)
    print("RAW INPUT:")
    print(raw_text)
    print()
    
    try:
        session.intake_json = run_intake_agent(raw_text)
        print("INTAKE JSON:")
        print(json.dumps(session.intake_json, indent=2))
        print()
    except Exception as e:
        print(f"ERROR in IntakeAgent: {e}")
        raise
    
    # ========================================================================
    # Step 2: ClarifierAgent - Generate follow-up questions
    # ========================================================================
    print("STEP 2: CLARIFIER AGENT")
    print("-" * 80)
    
    try:
        clarifier_output = run_clarifier_agent(raw_text, session.intake_json)
        session.clarifier_questions = clarifier_output.get("questions", [])
        
        print("CLARIFIER QUESTIONS:")
        if session.clarifier_questions:
            for i, q in enumerate(session.clarifier_questions, 1):
                print(f"{i}. {q}")
        else:
            print("(No questions generated)")
        print()
    except Exception as e:
        print(f"ERROR in ClarifierAgent: {e}")
        raise
    
    # ========================================================================
    # Step 3: Auto-answer questions (for demo)
    # ========================================================================
    print("STEP 3: AUTO ANSWERS (DEMO)")
    print("-" * 80)
    
    session.clarifier_answers = auto_answer_clarifier_questions(
        session.clarifier_questions
    )
    
    print("AUTO ANSWERS:")
    if session.clarifier_answers:
        for q, a in session.clarifier_answers.items():
            print(f"Q: {q}")
            print(f"A: {a}")
            print()
    else:
        print("(No answers needed)")
    print()
    
    # ========================================================================
    # Step 4: SummaryAgent - Create doctor-ready visit note
    # ========================================================================
    print("STEP 4: SUMMARY AGENT")
    print("-" * 80)
    
    try:
        session.doctor_note = run_summary_agent(
            raw_text,
            session.intake_json,
            session.clarifier_answers
        )
        
        print("DOCTOR NOTE:")
        print(session.doctor_note)
        print()
    except Exception as e:
        print(f"ERROR in SummaryAgent: {e}")
        raise
    
    # ========================================================================
    # Step 5: RoutingAgent - Suggest doctor types and tests
    # ========================================================================
    print("STEP 5: ROUTING AGENT")
    print("-" * 80)
    
    try:
        session.routing_guidance = run_routing_agent(
            raw_text,
            session.intake_json
        )
        
        print("ROUTING GUIDANCE:")
        doctors = session.routing_guidance.get("recommended_doctors", [])
        if doctors:
            print("\nRecommended Doctor Types:")
            for i, doc in enumerate(doctors, 1):
                print(f"{i}. {doc.get('type', 'Unknown')}")
                if doc.get('reason'):
                    print(f"   Reason: {doc['reason']}")
        
        tests = session.routing_guidance.get("possible_test_categories", [])
        if tests:
            print("\nPossible Test Categories:")
            for i, test in enumerate(tests, 1):
                print(f"{i}. {test.get('category', 'Unknown')}")
                if test.get('purpose'):
                    print(f"   Purpose: {test['purpose']}")
        
        urgency = session.routing_guidance.get("urgency_note", "")
        if urgency:
            print(f"\n{urgency}")
        
        print()
    except Exception as e:
        print(f"ERROR in RoutingAgent: {e}")
        # Don't raise - routing is optional
        session.routing_guidance = {}
    
    # ========================================================================
    # Step 6: EvalAgent - Evaluate note quality
    # ========================================================================
    print("STEP 6: EVAL AGENT (CRITIC)")
    print("-" * 80)
    
    try:
        session.eval_result = run_eval_agent(session.doctor_note)
        
        print("EVAL JSON:")
        print(json.dumps(session.eval_result, indent=2))
        print()
    except Exception as e:
        print(f"ERROR in EvalAgent: {e}")
        raise
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Symptoms extracted: {len(session.intake_json.get('symptoms', []))}")
    print(f"  - Questions generated: {len(session.clarifier_questions)}")
    print(f"  - Doctor types suggested: {len(session.routing_guidance.get('recommended_doctors', []))}")
    print(f"  - Note quality score: {session.eval_result.get('score', 'N/A')}/10")
    print()
    
    return session


def run_niracare_with_user_answers(
    raw_text: str,
    user_answers: Dict[str, str]
) -> NiraSession:
    """
    Runs NiraCare pipeline with user-provided answers to clarifier questions.
    
    This is an alternative to the demo function that allows real user input.
    Useful for testing with actual answers instead of auto-generated ones.
    
    Args:
        raw_text: Raw free-text description from user
        user_answers: Dictionary mapping questions to user-provided answers
        
    Returns:
        NiraSession object containing all outputs
    """
    session = NiraSession(raw_text=raw_text)
    
    # Run IntakeAgent
    session.intake_json = run_intake_agent(raw_text)
    
    # Run ClarifierAgent
    clarifier_output = run_clarifier_agent(raw_text, session.intake_json)
    session.clarifier_questions = clarifier_output.get("questions", [])
    
    # Use user-provided answers
    session.clarifier_answers = user_answers
    
    # Run SummaryAgent
    session.doctor_note = run_summary_agent(
        raw_text,
        session.intake_json,
        session.clarifier_answers
    )
    
    # Run EvalAgent
    session.eval_result = run_eval_agent(session.doctor_note)
    
    return session

