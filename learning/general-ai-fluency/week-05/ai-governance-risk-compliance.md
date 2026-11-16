# W5 Event: Who Is Watching the Robot? — AI Governance, Security, Risk & Compliance

- **Track**: FlyRank Internship · General AI Fluency · Week 5 (cross-track learning note)
- **Speaker**: Anes Paraganlija
- **Recording**: [YouTube](https://www.youtube.com/watch?v=AXDwPosCqU8)
- **Transcript supplied with the course**: [`W5-event-ai-governance-risk-compliance-transcript.txt`](./W5-event-ai-governance-risk-compliance-transcript.txt)

## What the session is about

The session asks who is accountable when an AI system affects a person. It uses decisions in hiring, lending, healthcare, and justice to make the point: an organization cannot hand responsibility to a model just because the model produced a score or recommendation. People need to decide where AI may be used, who reviews consequential outputs, how risks are checked, and how problems are handled.

The speaker’s practical message is to build governance, security, and risk controls alongside the product. Governance should make responsibilities and decision paths clear; security protects systems and data; risk work identifies and reduces possible harms; compliance keeps evidence that required controls and obligations are being met. These areas overlap, but they answer different questions.

## Main ideas

### AI creates risks that need active oversight

The talk highlights bias and discrimination, fabricated or misleading answers, privacy exposure, attacks such as prompt injection and data poisoning, and misuse at scale. Model confidence is not proof that an answer is correct. Guardrails can reduce risk, but they do not guarantee that a system will never fail; teams also need monitoring, escalation, and recovery plans.

Human oversight should be meaningful. A reviewer needs the authority, information, and time to question an AI recommendation. A person who merely approves every output without understanding it is not an effective safeguard.

### Regulation and standards are different tools

The speaker introduces the EU AI Act as a risk-based law. The European Commission describes categories ranging from prohibited practices and high-risk systems to transparency requirements and minimal-risk uses. Requirements depend on the system’s role and the organization’s role; consult the Commission’s current material before making a compliance decision. [European Commission: AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

The transcript says “ISO 4201” in places; the standard it means is **ISO/IEC 42001:2023**, an organizational AI management system standard. It provides a way to establish and continually improve AI management processes; it is not itself a law. [ISO: ISO/IEC 42001](https://www.iso.org/standard/42001)

The talk also introduces the **NIST AI Risk Management Framework (AI RMF 1.0)** and its four functions: **Govern, Map, Measure, Manage**. The framework helps organizations structure risk work across an AI system’s lifecycle. NIST describes it as voluntary guidance, not a certification or regulation. [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/AI/NIST.AI.100-1.pdf)

For application security, OWASP’s **Top 10 for LLM Applications 2025** gives teams a practical list of common LLM application risks to consider during design and testing. [OWASP GenAI Security Project](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)

### Examples from the presentation

The speaker discusses Amazon’s discontinued hiring-screening experiment and an Air Canada chatbot dispute to illustrate how historical data can encode bias and how an organization remains responsible for what it deploys. These are examples used in the recording, not a complete legal analysis. The general lesson is to test systems in their actual context and provide a path for people to challenge consequential outcomes.

## Applying this to the Week 5 Study Coach

The Study Coach works with course notes and can help prepare a study pack. Its risks are smaller than automated hiring or credit decisions, but the same habits apply:

| Risk | Practical control for this agent |
| --- | --- |
| It invents an explanation or citation | Ground answers in retrieved notes, cite the source, and say when the notes do not answer the question. |
| A note contains malicious or irrelevant instructions | Treat retrieved text as data, not as authority to change the agent’s instructions; test prompt-injection examples. |
| Private study material is exposed or changed unexpectedly | Keep retrieval scoped to the course workspace and use read-only access for the core task. |
| A generated study pack is saved without review | Require human approval before writing or publishing it. |
| A failure is hard to investigate | Keep a run record with the request, sources used, tool actions, and final result, while avoiding unnecessary sensitive content. |

In the FL-07 Study Coach build, the documented design uses read tools and a human approval gate for the study-pack writer. Those controls limit what the agent can do, but they do not replace checking its answers and tool behavior during evaluation.

## Takeaway

Before connecting a model to real data or actions, name the people affected, the decisions the system can influence, the likely failure modes, and the human response when something goes wrong. Then test those controls with ordinary and adversarial examples and keep evidence of what happened.

## Sources

- [Recording: Who Is Watching the Robot?](https://www.youtube.com/watch?v=AXDwPosCqU8)
- [European Commission: AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [ISO: ISO/IEC 42001:2023](https://www.iso.org/standard/42001)
- [NIST: AI Risk Management Framework 1.0](https://nvlpubs.nist.gov/nistpubs/AI/NIST.AI.100-1.pdf)
- [OWASP: Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)
