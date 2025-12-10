from typing import Dict, Sequence

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handle missing dependency gracefully
    OpenAI = None

COMPOSE_PROMPT = """
You are JOVIA — a psychological astrologer.
You transform fragmented rule-based outputs into a poetic, insightful,
psychologically layered interpretation.

Structure:
- Cause
- Mechanism
- Effect
- Shadow
- Potential

Rules:
- Do not repeat fragments exactly.
- Rewrite naturally.
- Keep the flow cohesive.
- Tone: psychological, evocative, elegant.
"""


class LlmNarrativeBuilder:
    """
    Premium AI-based narrative builder.
    """

    def __init__(self, model="gpt-4o-mini"):
        if OpenAI is None:
            raise RuntimeError("OpenAI SDK is not installed.")
        self.client = OpenAI()
        self.model = model

    def build_all(self, interpretation: Dict[str, Sequence[str]]) -> Dict[str, str]:
        final = {}
        for category, fragments in interpretation.items():
            final[category] = self.build_paragraph(fragments)
        return final

    def build_paragraph(self, fragments: Sequence[str]) -> str:
        if not fragments:
            return ""

        joined = "\n".join(fragments)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": COMPOSE_PROMPT},
                {"role": "user", "content": f"Fragments:\n{joined}\n\nWrite the final paragraph:"},
            ],
            temperature=0.45,
        )

        return response.choices[0].message.content.strip()
