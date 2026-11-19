# Week 9: Launch & Keep Building — Graduation & Compounding Platform

## Session & Milestone Details

- **Title:** Launch & Keep Building
- **Track:** General AI Fluency (Cross-cutting with Backend AI Engineering)
- **Portal Date:** September 4, 2026, 2:00 PM (Africa/Lagos GMT+01:00)
- **Portal Duration:** 90 minutes (Recorded Milestone Session)
- **Event Link:** [Launch & Keep Building](https://internship.flyrank.ai/intern/events/CUSTOM-MQX0MUZC-B30B81AE)
- **Companion Curriculum Guide:** [Week 9 Guide · Launch & Keep Building (Checkpoint 2)](https://aifluency.flyrank.ai/week-09.html)
- **Phase:** Submit Gate · **Checkpoint 2** (Hardening Review & Launch Gate)

---

## 1. Executive Summary: Closing the Week 1 Loop

In Week 1 of the FlyRank AI Internship, the core premise was established:
> **"You don't study your way into the AI world, you build your way in."**

Week 9 represents the culmination and proof of that premise. Over nine weeks, interns moved from raw ideas to working APIs, scraped datasets, structured background jobs, durable Inngest workflows, and interactive frontends. 

The purpose of **Launch & Keep Building** is not merely to celebrate graduation, but to transform a class project into a **permanent, compounding career platform**:
1. **Adversarial Hardening**: Breaking the site on purpose and producing an honest audit of limits before launching to the public.
2. **Planting the Flag**: Moving to a permanent domain over HTTPS, setting up privacy-friendly analytics, and verifying social metadata.
3. **The Graduate Badge**: Displaying the FlyRank Graduate Badge in the footer linking to an immutable credential verification record.
4. **The Compounding Habit**: Establishing a concrete, repeatable 30-minute protocol to add new case studies as new projects ship, ensuring the portfolio never goes stale.

---

## 2. The Three Core Pillars of Week 9

```
                            WEEK 9: LAUNCH & KEEP BUILDING
                                  (Checkpoint 2 Gate)
                                          │
         ┌────────────────────────────────┼────────────────────────────────┐
         ▼                                ▼                                ▼
   PILLAR 1: BREAK IT               PILLAR 2: LAUNCH               PILLAR 3: COMPOUND
• Attack empty & garbage inputs   • Point custom domain          • 30-min case study protocol
• Test cross-device & network     • Enforce HTTPS & DNS          • Three-beat story structure
• Triage: fix-now vs limitations  • Free privacy analytics       • Name next concrete project
• Honest disclosure list          • FlyRank graduate badge       • Calendar reminder + AI workspace
```

---

## 3. Pillar 1: Break Your Own Site (Diligence Over Polish)

Anyone can demo a software project along the "happy path"—when the user types the expected input, the network is pristine, and the buttons are clicked once. 

The hallmark of a professional AI engineer is **Diligence**: knowing precisely where your system cracks under pressure and documenting those limits honestly.

### The Four Adversarial Attack Vectors
1. **Garbage & Whitespace Payloads**:
   - Submitting whitespace-only strings (`"   "`).
   - Submitting malformed email structures (`user@`, `@domain`, `name..name@test`).
   - Flooding textareas with oversized payloads (>2,000 to 50,000 characters).
2. **Race Conditions & Double-Submits**:
   - Clicking the submit button multiple times rapidly before server response.
   - Pressing `Enter` repeatedly while an asynchronous request is in flight.
3. **Network Degradation & Infinite Hangs**:
   - Simulating 3G network drops or stalled edge connections.
   - Verifying that network abort controllers trigger clean fallbacks rather than freezing on indefinite loading spinners.
4. **Link Integrity & Responsive Device Scaling**:
   - Automated curl sweeps across all relative and external URLs to catch `404 Not Found` drifts.
   - Stress-testing responsive layouts on small viewports (320px–375px) to catch text overlaps and button clipping.

### The Professional Triage Framework
Findings must be categorized without evasion:
- **Fix-Now Findings**: Architectural vulnerabilities, unhandled promise rejections, race conditions, missing input bounds, and broken navigation links. These **must** be remediated in code prior to launch.
- **Known Limitations**: Structural constraints consciously accepted for the current release (e.g., third-party free-tier quotas, search engine indexing delays, or direct curl bypasses of client-side validation). These must be named explicitly in documentation.

> *"The longest honest 'where it breaks' list in the cohort is the best work, not the worst. The engineer who knows their system's limits is the one employers trust."*

---

## 4. Pillar 2: Plant Your Flag (Domain, Analytics & Graduate Badge)

### 1. Custom Domain & HTTPS
Moving from a default hosting subdomain (`xyz.netlify.app` or `abc.vercel.app`) to an owned personal domain (e.g., `jezrealmomoh.dev` or `jezreal.dev`) changes the nature of the portfolio from a temporary school submission to a permanent digital home.
- **DNS Records**: Configuring `A` records (apex) and `CNAME` records (`www`) pointing to the edge CDN.
- **TLS/HTTPS**: Verifying automated Let's Encrypt certificate issuance.
- **Fallback Rule**: A clean, customized subdomain is acceptable only when financial constraints exist, provided HTTPS is strictly enforced.

### 2. Social Launch Hygiene
When a portfolio link is shared in Slack, LinkedIn, X, or email, it must render an intentional, informative preview card:
- `<link rel="canonical">` to prevent duplicate indexing.
- Open Graph tags (`og:title`, `og:description`, `og:image`, `og:url`).
- Twitter Card tags (`twitter:card`, `twitter:image`).
- Dedicated 1200×630px social card image clearly communicating the engineer's proof statement and role.

### 3. Lightweight, Privacy-Friendly Analytics
Setting up analytics transforms passive hope into empirical knowledge. The curriculum emphasizes privacy-friendly solutions that require no intrusive cookie banners or GDPR tracking consent:
- **Cloudflare Web Analytics** (free, zero-cookie, edge-based).
- **Plausible Analytics** (open-source, lightweight, under 1 KB script).

### 4. The FlyRank Graduate Badge
Installing the official FlyRank Graduate Badge in the site footer provides proof of work:
- Visual badge linking to the intern's verified verification URL.
- Confirms successful passage through both Checkpoint 1 (Design Review) and Checkpoint 2 (Hardening Review).

---

## 5. Pillar 3: The Compounding Portfolio Habit

A portfolio that is never updated after graduation goes stale within six months. The difference between a class artifact and a compounding career platform is a **repeatable publishing habit**.

### The 30-Minute Three-Beat Case Study Addition Protocol
Whenever a new milestone or project is finished, add it using the standard Three-Beat structure:
1. **Beat 1: The Context & Problem Statement**: What was broken or missing, and why did it matter?
2. **Beat 2: The Architectural Seam & Stack**: What tools, APIs, and layered patterns were implemented? (Fast-door HTTP routes, Inngest durable steps, SQLite database, Pydantic validation).
3. **Beat 3: What It Does, Where It Breaks & Live Proof**: How does it perform, what are its verified limits, and where is the working repository or live demo?

### Preserving the AI Workspace
Do not discard the agent workspace or conversation context after graduation. The AI workspace already knows:
- Your personal identity kit and proof statement.
- Your chosen backend tech stack and coding conventions.
- Your typography, CSS variables, and HTML layout structure.

Preserving this workspace allows you to draft and format a new case study in minutes simply by asking:
> *"I just shipped project X. Here is the repository and README. Format this as my next portfolio case study matching my existing layout, three-beat structure, and CSS classes."*

---

## 6. Checkpoint 2 Evaluation Rubric (Pass / Revise)

To pass Checkpoint 2 and unlock graduation, the portfolio must satisfy six strict verification criteria:

| Criterion | Rubric Requirement | Verification in Jezreal Momoh's Portfolio |
| :--- | :--- | :--- |
| **1. Genuine Adversarial Testing** | Did the intern test edge cases beyond the happy path (empty forms, double-submits, slow networks)? | **PASS**: Full adversarial test log in [`portfolio/BREAK_YOUR_OWN_SITE.md`](../../../portfolio/BREAK_YOUR_OWN_SITE.md). Tested blank inputs, rapid clicks, 12s timeout, and 9 live links. |
| **2. Honest Triage** | Are fix-nows resolved in code and known limitations named openly? | **PASS**: 5 fix-nows fixed (input bounds, submit locks, cooldowns, AbortController timeout, OG card overlap). 5 limitations documented openly. |
| **3. Hardening Review** | Did the review pass and address all required must-fixes? | **PASS**: Hardening review documented with verified code commits (`c903cc1`). |
| **4. Live Domain & HTTPS** | Is the site live over HTTPS with valid certificates? | **PASS**: Live at [`https://jezreal-momoh-portfolio.netlify.app`](https://jezreal-momoh-portfolio.netlify.app) with valid Let's Encrypt TLS. |
| **5. Launch Hygiene & Badge** | Are page titles, favicon, OG cards, and the graduate badge in place? | **PASS**: Favicon (`jm-favicon.svg`), 1200×630 OG Card (`og-card.png`), JSON-LD Person schema, and footer graduate badge. |
| **6. Compounding Plan** | Does a concrete plan exist with a named next piece and reminder? | **PASS**: [`portfolio/HOW_TO_ADD_A_CASE_STUDY.md`](../../../portfolio/HOW_TO_ADD_A_CASE_STUDY.md) + [`Impact_Project_Portfolio_Habit_Jezreal_Momoh.pdf`](../../../portfolio/Impact_Project_Portfolio_Habit_Jezreal_Momoh.pdf) with named next piece (`BE-09 AI Decision Flow`). |

---

## 7. Next Action Items for Graduation

1. **Portfolio Footer Update**: Verify FlyRank graduate badge markup is visible in `site/index.html`.
2. **Capstones & Showcase**: Prepare the 3-minute screen-recorded demo walking through the live portfolio and dynamic contact form for Week 10.
3. **Publish Next Case Study**: Add **BE-09 (AI Decision Flow with React Flow + Inngest)** as the first post-graduation portfolio project using the 30-minute protocol.
