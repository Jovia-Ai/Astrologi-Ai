# Slot & Skeleton Guidelines

These instructions lock the behavior of the slot → skeleton pipeline so that downstream consumers can rely on consistent, regulator-driven narratives.

## 1. Slots are scene descriptors

- **Slots only describe inner scenes.** They must stay away from verbs, explicit times, causal connectors, or user-facing narratives. Think: *yük / baskı / gerilim / çatışma / ihtiyaç / sahne* (e.g., “artan kontrol baskısı”, “yoğun öz-eleştiri yükü”).
- **Slots are not standalone output.** They are raw input for the skeleton layer; they never surface to end users as-is.
- **Slot text must be cleaned.** Phase‑1/Phase‑2 text messages must be rewritten to this descriptor format before they travel to the skeleton builder. Semantic normalizer logic enforces this by stripping connectors, subjects, verbs, and temporal markers.

## 2. Skeleton remains the single storyteller

- **All verbs, times, and flows live only inside the skeleton.** The slot layer simply announces the scene; the skeleton composes the sentence.
- **Slot → meaning modulation only.** Avoid giving slots any additional responsibilities beyond describing the scene that the skeleton will narrate.

## 3. Failure behavior is deliberate silence

- If fewer than two slots are available for a domain, **do not produce half paragraphs or single sentences**. Either stay silent or return a short, neutral fallback that focuses on regulation.
- This is a deliberate product guardrail: incomplete slot data should never leak into a partial story.

## 4. Implementation checklist (locked)

1. **Slot rewrite:** Phase‑1 and Phase‑2 slot text must be rewritten into scene descriptors with no verbs, no explicit time, and no cause/effect language.
2. **Guardrails stay:** Verb detection and adjective false-positive logic remain in place; slot quality follows the guardrails.
3. **Narrative authority:** The skeleton builder (e.g., `JoviaSemanticNarrativeBuilder`) still composes the final prose using the clean slots.
4. **Failure mode:** `<2 slots → silence or neutral fallback; never partial paragraph`.
5. **Domain rollout:** Start with Identity, secure PASS, then expand to Psychology, Relationships, etc.

