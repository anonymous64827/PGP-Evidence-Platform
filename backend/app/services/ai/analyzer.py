from google import genai
from pydantic import BaseModel, Field


class EvidenceAnalysis(BaseModel):
    evidence_type: str = Field(
        description="Type of evidence, such as incident report, document, image, etc."
    )

    summary: str = Field(
        description="Concise factual summary of the evidence."
    )

    key_entities: list[str] = Field(
        description="People, vehicles, objects, organizations, or other entities explicitly mentioned."
    )

    important_dates: list[str] = Field(
        description="Dates or times explicitly present in the evidence."
    )

    locations: list[str] = Field(
        description="Locations explicitly mentioned in the evidence."
    )

    important_observations: list[str] = Field(
        description="Important factual observations directly supported by the evidence."
    )

    potentially_relevant_information: list[str] = Field(
        description="Information that may be useful for investigation, without inventing facts."
    )

    confidence_level: str = Field(
        description="AI confidence level: HIGH, MEDIUM, or LOW."
    )


def analyze_text(text: str) -> EvidenceAnalysis:

    client = genai.Client()

    prompt = f"""
You are an AI evidence analysis assistant for a digital forensic
evidence management platform.

Analyze the evidence below.

IMPORTANT RULES:

- Only use information explicitly present in the evidence.
- Never invent names, dates, locations, objects, or events.
- If something is not available, use an empty list.
- Separate factual observations from assumptions.
- Do not make legal conclusions.
- The analysis is AI-assisted and must remain factual.

Evidence:

{text}
"""

    interaction = client.interactions.create(
        model="gemini-3.7-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": EvidenceAnalysis.model_json_schema()
        }
    )

    return EvidenceAnalysis.model_validate_json(
        interaction.output_text
    )