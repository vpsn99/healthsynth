# Contributing to HealthSynth

Thank you for your interest in contributing.

HealthSynth aims to become a high-quality open-source healthcare commercial analytics simulation platform.
HealthSynth is an evolving open-source project. Contributions that improve learning, realism, extensibility, or developer experience are particularly appreciated.

Quality matters more than speed.

---

# Before You Start

Please read:

- VISION.md
- ARCHITECTURE.md
- DATA_MODEL.md

Understanding the project's philosophy is more important than understanding the code.

---

# Guiding Principles

Every contribution should improve at least one of the following:

- business realism
- usability
- maintainability
- documentation
- reproducibility

---

# Design Principles

Prefer:

- explicit business rules
- deterministic generation
- configuration over hardcoded values
- readable code over clever code
- modular components

Avoid:

- magic numbers
- hidden assumptions
- tightly coupled modules

---

# Project Structure

HealthSynth
│
├── Core
│   Commercial simulation engine
│
├── Studio
│   Interactive Streamlit application
│
├── Notebooks
│   Learning and demonstrations
│
└── Configuration
    YAML-based business knowledge

---

# Ways to contribute

HealthSynth welcomes contributions in many forms:

• Commercial simulation logic
• HealthSynth Studio
• Documentation
• Jupyter notebooks
• Unit tests
• New commercial scenarios
• Performance improvements
• Bug fixes
• Examples and tutorials

---

# Scenarios

Every scenario should represent a believable business event.

Good examples:

- Product Launch
- Territory Realignment
- Loss of Exclusivity

Poor examples:

- Randomly increase prescriptions by 20%

Business behaviour should emerge naturally from the simulation.

## Adding New Scenarios

Prefer implementing business behaviour through configuration rather than hardcoding logic.

Commercial events should influence the simulation naturally instead of directly modifying output datasets.

New scenarios should include:

• YAML profile
• Tests
• Documentation
• Notebook (if appropriate)

## Documentation
Documentation improvements are always welcome.

Examples include:

- README improvements
- Architecture documentation
- Tutorials
- Notebook explanations
- API documentation
  
---

# Pull Requests

Before submitting a PR, please ask:

- Does this improve realism?
- Does this preserve deterministic generation?
- Does this simplify learning?
- Does it align with the project vision?

---

# Community

HealthSynth welcomes contributions from:

- Engineers
- Data Scientists
- Architects
- Healthcare Analytics Professionals
- Students

If you're unsure whether something belongs in the project, open a discussion before implementing it.

We'd much rather discuss ideas early than review large pull requests that don't fit the project's direction.