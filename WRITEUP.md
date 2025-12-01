# NiraCare: Multi-Agent AI Assistant for Women's Health Communication

**Kaggle Competition:** Agents Intensive – Capstone Project, Agents for Good track

---

## My Inspiration

As a woman myself, I've experienced firsthand the frustration of trying to communicate health concerns during doctor visits. I've sat in exam rooms, my mind going blank when asked to describe symptoms I've been experiencing for weeks. I've watched friends and family members struggle to articulate their concerns—especially around reproductive health, menstrual cycles, and chronic conditions—only to leave appointments feeling unheard or misunderstood.

The women around me have shared countless stories: forgetting crucial details in the moment, feeling dismissed when symptoms seem "too vague," struggling to find the right medical terminology, and leaving appointments with incomplete documentation that doesn't capture the full picture of what they're experiencing.

This project is deeply personal. It's born from my own experiences and the experiences of women I care about. NiraCare is my attempt to bridge that communication gap—to give women a tool that helps them prepare, organize their thoughts, and ensure their voices are heard clearly in healthcare settings. It's not about replacing the doctor-patient relationship; it's about empowering women to communicate more effectively so they can receive the care they deserve.

---

## Problem Statement

Women often struggle to communicate their health symptoms effectively during doctor visits. When experiencing health concerns, especially those related to reproductive health, menstrual cycles, or chronic conditions, patients frequently lack structure in describing symptoms, feel overwhelmed by emotional concerns, forget important details due to stress, struggle with medical terminology, and experience communication gaps that result in misdiagnosis or delayed care.

This problem is particularly acute for women's health issues, where symptoms can be cyclical, complex, and deeply personal. The consequences include incomplete medical records, missed diagnoses, patient frustration, inefficient use of appointment time, and reduced quality of care.

**Why this matters:** Effective communication between patients and healthcare providers is fundamental to quality care. When patients can clearly articulate their symptoms, doctors can make more accurate assessments, order appropriate tests, and provide better treatment. NiraCare addresses this critical communication gap by helping patients prepare structured, comprehensive visit notes before their appointments.

---

## Why Agents?

Multi-agent systems are the **perfect solution** for this problem because:

### 1. **Separation of Concerns**

Each agent has a specialized role: **IntakeAgent** extracts structured data, **ClarifierAgent** identifies gaps and generates questions, **SummaryAgent** synthesizes documentation, **RoutingAgent** provides care pathway guidance, and **EvalAgent** ensures quality. This separation ensures each agent excels at its specific task.

### 2. **Iterative Refinement**

The architecture enables an iterative process: Extract symptoms → Identify gaps → Ask questions → Refine understanding → Create comprehensive note. This mimics real medical intake processes where information is gathered progressively.

### 3. **Quality Control & Safety**

The EvalAgent provides objective quality assessment, creating a feedback loop that ensures professional standards. By separating concerns, we can enforce safety constraints more effectively—each agent has specific instructions to avoid diagnosis or treatment suggestions, and the critic can flag inappropriate content.

### 4. **Modularity and Transparency**

The agent-based architecture enables easy extension (new agents, specialty adaptations, EHR integration) while maintaining transparency—each agent's output is visible and traceable, building trust and enabling verification.

**Why not a single agent?** A monolithic approach would struggle with maintaining consistent JSON structure while generating natural language, balancing multiple tasks, providing quality control, and ensuring safety constraints across all outputs.

---

## What You Created

### Overall Architecture

NiraCare is a **5-agent orchestration system** that transforms unstructured symptom descriptions into doctor-ready visit notes:

```
User Input → IntakeAgent → ClarifierAgent → User Answers → SummaryAgent → RoutingAgent → EvalAgent → Complete Session
```

### Agent Details

**IntakeAgent:** Extracts structured symptoms (JSON) from raw text, including name, severity, frequency, timing, and cycle relation.

**ClarifierAgent:** Identifies information gaps and generates doctor-style follow-up questions (JSON). Never answers questions, only asks them.

**SummaryAgent:** Synthesizes raw text, structured symptoms, and clarifier answers into a formatted visit note with sections: Chief complaint, History of present illness, Impact on daily life, Patient questions. Absolutely no diagnosis, treatment, or medical advice.

**RoutingAgent:** Suggests appropriate doctor types and general test categories (JSON) based on symptoms. Only general guidance, no specific diagnoses.

**EvalAgent (Critic):** Evaluates visit note quality, outputting score (0-10), missing fields, and improvement suggestions (JSON). Ensures completeness, clarity, and presence of key information.

### Session State Management

All outputs are tracked in a `NiraSession` dataclass: `raw_text`, `intake_json`, `clarifier_questions`, `clarifier_answers`, `doctor_note`, `routing_guidance`, `eval_result`. This demonstrates **memory/session state**—a key competition requirement.

---

## Demo

### Example Input

```
I've been having really bad cramps for the past two weeks. They started 
around my period but haven't gone away. The pain is so intense sometimes 
I can't focus at work. It's worse in the morning and gets better by evening. 
I'm also feeling really tired all the time, like I can't get enough sleep.
```

### Pipeline Output

**IntakeAgent** extracts structured symptoms:
```json
{
  "symptoms": [
    {"name": "cramps", "severity": "severe", "frequency": "daily", 
     "since_when": "2 weeks ago", "cycle_related": "yes"},
    {"name": "fatigue", "severity": "moderate", "frequency": "daily"}
  ]
}
```

**ClarifierAgent** generates questions:
```json
{"questions": ["Can you describe the exact location of the cramps?", 
               "Have you noticed anything that makes them better or worse?"]}
```

**SummaryAgent** creates visit note:
```
CHIEF COMPLAINT: Severe abdominal cramps for 2 weeks, cycle-related, 
accompanied by fatigue.

HISTORY OF PRESENT ILLNESS: Onset 2 weeks ago around period time. 
Pattern: Daily, worse in morning, improves by evening. Severity: Severe, 
impacts work focus. Associated factors: Fatigue, sleep issues.
```

**RoutingAgent** suggests care pathways:
```json
{
  "recommended_doctors": [
    {"type": "Primary Care Physician", "reason": "Initial evaluation"},
    {"type": "Gynecologist", "reason": "Period-related concerns"}
  ],
  "possible_test_categories": [
    {"category": "Blood tests", "purpose": "Check hormone levels"},
    {"category": "Pelvic imaging", "purpose": "Visualize organs if needed"}
  ]
}
```

**EvalAgent** evaluates quality:
```json
{"score": 8, "missing_fields": ["Cramp location details"], 
 "suggested_improvement": "Add specific details about cramp location."}
```

### How to Run

```bash
python3 run_interactive.py
```

Enter symptoms, answer follow-up questions, and receive structured extraction, doctor-ready note, routing guidance, and quality evaluation.

---

## The Build

### Technologies Used

- **Google Gemini 2.5 Flash** - Powers all agents (meets competition requirement)
- **Google Generative AI SDK** - Direct API access for reliable operation
- **Python 3.9+** - Core language
- **Python-dotenv** - Environment variable management
- **Dataclasses** - Session state management

### Architecture Decisions

**Why Gemini SDK Instead of ADK?** Direct SDK access avoids session management complexities, is easier to debug, still meets Gemini requirement, and performs faster without ADK overhead.

**Why Multiple Agents?** Modularity enables independent improvement, transparency shows each agent's output to judges, safety is easier to enforce per agent, and extensibility allows easy addition of new agents.

**Why JSON for Structured Outputs?** Ensures consistent parsing, enables interoperability with other systems, allows programmatic validation, and provides clarity for judges inspecting outputs.

### Code Structure

```
NiraCare/
├── niracare_agents.py            # All 5 agent definitions
├── niracare_pipeline.py          # Orchestration & session management
├── run_interactive.py            # Interactive terminal interface
└── requirements.txt              # Dependencies
```

### Key Features

1. **Pure JSON Outputs:** Clean JSON without markdown wrappers
2. **Error Handling:** Comprehensive error handling with helpful messages
3. **Type Safety:** Full type hints throughout codebase
4. **Safety Constraints:** Multiple layers preventing diagnosis/treatment suggestions
5. **Session State:** Complete tracking of all intermediate outputs

### Development Process

1. **Agent Design:** Defined clear roles and responsibilities
2. **Prompt Engineering:** Crafted detailed instructions for correct output formats
3. **JSON Extraction:** Built robust parsing for various response formats
4. **Pipeline Integration:** Orchestrated agents in logical sequence
5. **Testing:** Validated with multiple symptom descriptions
6. **Safety Review:** Ensured no diagnostic or treatment content

---

## If I Had More Time, This Is What I'd Do

### Short-term Improvements

1. **Enhanced RoutingAgent:** More specific doctor recommendations based on symptom patterns, insurance network integration, location-based suggestions.

2. **Better Question Generation:** Context-aware questions adapting to previous answers, prioritized by importance, with skip options.

3. **Multi-language Support:** Translation agent for non-English speakers, cultural sensitivity, localized medical terminology.

4. **Export Functionality:** PDF generation, patient portal integration, email/SMS delivery.

### Medium-term Enhancements

5. **EHR Integration:** Direct upload to Epic/Cerner, HL7/FHIR compatibility, secure API connections.

6. **Voice Input:** Speech-to-text for symptom descriptions, natural conversation flow, accessibility improvements.

7. **Mobile App:** Native iOS/Android applications, offline capability, push notifications.

8. **Advanced Analytics:** Symptom pattern recognition, trend analysis for chronic conditions, anonymized population health insights.

### Long-term Vision

9. **Provider Dashboard:** Doctors review notes before appointments, flag areas needing clarification, pre-populate EHR fields.

10. **AI-Powered Follow-up:** Automated check-ins, medication adherence tracking, symptom progression monitoring.

11. **Specialty Versions:** NiraCare Cardiology, Pediatrics, Mental Health—each with specialized agents and workflows.

12. **Technical Improvements:** Caching and optimization, A/B testing framework, cloud deployment with auto-scaling, HIPAA-compliant security enhancements.

---

## Conclusion

NiraCare demonstrates the power of multi-agent systems to solve real-world healthcare communication challenges. By breaking down medical documentation into specialized agent roles, we've created a system that improves patient-provider communication, reduces appointment inefficiencies, enhances care quality through better documentation, maintains strict safety standards, and provides transparent, traceable outputs.

The multi-agent architecture is not just a technical choice—it's essential for ensuring quality, safety, and extensibility in a healthcare context where accuracy and trust are paramount.

---

**Competition Requirements Met:**
- ✅ Google ADK/Gemini usage (Gemini 2.5 Flash)
- ✅ Multi-agent orchestration (5 agents)
- ✅ Memory/session state (NiraSession)
- ✅ Critic/Eval agent (EvalAgent)
- ✅ Safe design (no diagnosis/treatment)
- ✅ Kaggle-compatible
- ✅ Clear documentation

