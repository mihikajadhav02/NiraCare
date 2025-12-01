# NiraCare: Multi-Agent AI Assistant for Women's Health Communication

**Kaggle Competition:** Agents Intensive – Capstone Project, Agents for Good track

## My Inspiration

As a woman myself, I've experienced firsthand the frustration of trying to communicate health concerns during doctor visits. I've sat in exam rooms, my mind going blank when asked to describe symptoms I've been experiencing for weeks. I've watched friends and family members struggle to articulate their concerns—especially around reproductive health, menstrual cycles, and chronic conditions—only to leave appointments feeling unheard or misunderstood.

The women around me have shared countless stories: forgetting crucial details in the moment, feeling dismissed when symptoms seem "too vague," struggling to find the right medical terminology, and leaving appointments with incomplete documentation that doesn't capture the full picture of what they're experiencing.

This project is deeply personal. It's born from my own experiences and the experiences of women I care about. NiraCare is my attempt to bridge that communication gap—to give women a tool that helps them prepare, organize their thoughts, and ensure their voices are heard clearly in healthcare settings. It's not about replacing the doctor-patient relationship; it's about empowering women to communicate more effectively so they can receive the care they deserve.

## One-Line Description

NiraCare is a multi-agent AI assistant that converts messy, emotional symptom descriptions from women into a clear, structured, doctor-ready visit note. It is a communication helper, **NOT a diagnostic tool**.

## Problem Statement

Women often struggle to communicate their health symptoms effectively during doctor visits. Emotional, unstructured descriptions can lead to miscommunication and incomplete documentation. NiraCare bridges this gap by using specialized AI agents to extract, clarify, and structure symptom information into professional medical notes.

## Solution Architecture

NiraCare uses **5 specialized agents** working together in a coordinated pipeline:

### 1. **IntakeAgent**
- **Role:** Extracts structured symptom data from raw text
- **Input:** Free-text description of symptoms
- **Output:** Pure JSON with structured symptom list (name, severity, frequency, timing, cycle relation, notes)
- **Why separate agent:** Ensures consistent JSON structure and focuses solely on extraction

### 2. **ClarifierAgent**
- **Role:** Identifies information gaps and generates follow-up questions
- **Input:** Raw text + structured symptoms
- **Output:** Pure JSON with list of focused questions
- **Why separate agent:** Separates question generation from extraction, allowing iterative refinement

### 3. **SummaryAgent**
- **Role:** Synthesizes all information into a doctor-ready visit note
- **Input:** Raw text + structured symptoms + clarifier answers
- **Output:** Formatted visit note (chief complaint, history, impact, patient questions)
- **Why separate agent:** Focuses on documentation quality without mixing concerns with extraction

### 4. **RoutingAgent**
- **Role:** Suggests appropriate doctor types and general test categories
- **Input:** Raw text + structured symptoms
- **Output:** Pure JSON with recommended doctor types and possible test categories
- **Why separate agent:** Provides care pathway guidance without mixing with documentation

### 5. **EvalAgent (Critic)**
- **Role:** Evaluates note completeness and quality
- **Input:** Visit note from SummaryAgent
- **Output:** Pure JSON with score (0-10), missing fields, and improvement suggestions
- **Why separate agent:** Provides objective quality control and enables iterative improvement

## Key Features

✅ **Multi-Agent Orchestration:** 5 agents working in sequence  
✅ **Session State Management:** `NiraSession` dataclass tracks all intermediate outputs  
✅ **Critic Agent:** EvalAgent provides quality evaluation  
✅ **Routing Guidance:** Suggests appropriate doctor types and test categories  
✅ **Safe Design:** No diagnosis, no treatment suggestions, no disease probabilities  
✅ **Kaggle-Compatible:** Designed to run in Kaggle Notebooks with minimal edits  

## Safety Guarantees

- ❌ **NO** diagnosis or differential diagnosis
- ❌ **NO** treatment suggestions or medication recommendations
- ❌ **NO** disease probability estimates
- ❌ **NO** medical advice of any kind
- ✅ **ONLY** structured documentation and communication assistance

## Project Structure

```
NiraCare/
├── niracare_agents.py           # All 5 agent definitions using Gemini SDK
├── niracare_pipeline.py         # Orchestration and session management
├── run_interactive.py           # Interactive terminal interface
├── requirements.txt             # Python dependencies
├── WRITEUP.md                   # Competition writeup
└── README.md                    # This file
```

## Quickstart

### Prerequisites

- Python 3.9+
- Google API Key (set as environment variable)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (required)
# Option 1: Environment variable
export GOOGLE_API_KEY='your-api-key-here'

# Option 2: Create .env file (recommended for local development)
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

### Local Usage

**Interactive Mode (Recommended):**
```bash
python3 run_interactive.py
```

**Programmatic Usage:**
```python
from niracare_pipeline import run_niracare_with_user_answers

# Example symptom description
raw_text = """
I've been having really bad cramps for the past two weeks. They started 
around my period but haven't gone away. The pain is so intense sometimes 
I can't focus at work.
"""

# Run the complete pipeline (interactive questions)
session = run_niracare_with_user_answers(raw_text)

# Access results
print(session.intake_json)         # Structured symptoms
print(session.clarifier_questions) # Follow-up questions
print(session.doctor_note)         # Final visit note
print(session.routing_guidance)    # Doctor & test suggestions
print(session.eval_result)         # Quality evaluation
```

### Kaggle Notebook Setup

1. **Upload Files:**
   - Upload `niracare_agents.py` and `niracare_pipeline.py` to your notebook's input files
   - Or copy their contents into notebook cells

2. **Set Environment Variable:**
   - Go to Kaggle notebook settings → Environment variables
   - Add `GOOGLE_API_KEY` with your API key value

3. **Run Example:**
   ```python
   from niracare_pipeline import run_niracare_with_user_answers
   
   session = run_niracare_with_user_answers("Your symptom description here...")
   ```

## How It Works

### Multi-Agent Pipeline Flow

```
User Input (raw text)
    ↓
[IntakeAgent] → Structured Symptoms (JSON)
    ↓
[ClarifierAgent] → Follow-up Questions (JSON)
    ↓
[User Answers] → Answers to Questions
    ↓
[SummaryAgent] → Doctor-Ready Visit Note
    ↓
[RoutingAgent] → Doctor Types & Test Suggestions (JSON)
    ↓
[EvalAgent] → Quality Evaluation (JSON)
    ↓
Complete Session State
```

### Session State (`NiraSession`)

The pipeline maintains state through a `NiraSession` dataclass containing:
- `raw_text`: Original user input
- `intake_json`: Structured symptoms from IntakeAgent
- `clarifier_questions`: Questions from ClarifierAgent
- `clarifier_answers`: User-provided answers
- `doctor_note`: Final visit note from SummaryAgent
- `routing_guidance`: Doctor types and test suggestions from RoutingAgent
- `eval_result`: Quality evaluation from EvalAgent

## Why Multi-Agent?

This project demonstrates **true multi-agent orchestration** rather than a single monolithic prompt:

1. **Separation of Concerns:** Each agent has a single, well-defined responsibility
2. **Modularity:** Agents can be improved independently
3. **Quality Control:** EvalAgent provides objective feedback loop
4. **Extensibility:** Easy to add new agents (e.g., translation agent, formatting agent)
5. **Transparency:** Judges can see each agent's output and understand the workflow

## Technical Details

- **Framework:** Google Generative AI SDK (Gemini-powered)
- **Models:** Gemini 2.5 Flash
- **Output Format:** Pure JSON (no markdown wrappers) for structured outputs
- **Error Handling:** JSON parsing with helpful error messages
- **Type Safety:** Full type hints throughout codebase

## Competition Requirements Met

✅ **Google Gemini:** All agents use Gemini 2.5 Flash  
✅ **Multi-Agent:** 5 agents (Intake, Clarifier, Summary, Routing, Eval)  
✅ **Memory/Session:** `NiraSession` dataclass maintains state  
✅ **Critic Agent:** EvalAgent evaluates output quality  
✅ **Safe:** No diagnosis, treatment, or medical advice  
✅ **Kaggle-Compatible:** Runs in notebooks with minimal edits  
✅ **No Hardcoded Keys:** Uses `GOOGLE_API_KEY` environment variable  

## Example Output

```
STEP 1: INTAKE AGENT
RAW INPUT:
I've been having really bad cramps...

INTAKE JSON:
{
  "symptoms": [
    {
      "name": "abdominal cramps",
      "severity": "severe",
      "frequency": "daily",
      "since_when": "2 weeks ago",
      "cycle_related": "yes",
      "notes": "worse in morning, better by evening"
    }
  ]
}

STEP 2: CLARIFIER AGENT
CLARIFIER QUESTIONS:
1. How long do the cramps typically last each day?
2. Are there any specific triggers that make them worse?
...

STEP 4: SUMMARY AGENT
DOCTOR NOTE:
CHIEF COMPLAINT:
Severe abdominal cramps for 2 weeks, cycle-related...

STEP 5: ROUTING AGENT
ROUTING GUIDANCE:
Recommended Doctor Types:
1. Primary Care Physician
2. Gynecologist
Possible Test Categories:
1. Blood tests
2. Pelvic imaging

STEP 6: EVAL AGENT (CRITIC)
EVAL JSON:
{
  "score": 8,
  "missing_fields": [],
  "suggested_improvement": "Note is comprehensive..."
}
```

## License

This project is created for the Kaggle Agents Intensive Capstone Project.

## Contact

For questions about this implementation, please refer to the Kaggle competition guidelines.

