from backend.app.services.ai.analyzer import analyze_text


file_path = "evidence_vault/EVID-2C0E96FF_test_evidence.txt"

with open(file_path, "r", encoding="utf-8") as file:
    evidence_text = file.read()


result = analyze_text(evidence_text)


print("\n===== REAL EVIDENCE AI ANALYSIS =====\n")

print("Evidence Type:", result.evidence_type)
print("Summary:", result.summary)
print("Key Entities:", result.key_entities)
print("Important Dates:", result.important_dates)
print("Locations:", result.locations)
print("Observations:", result.important_observations)
print(
    "Relevant Information:",
    result.potentially_relevant_information
)
print("Confidence:", result.confidence_level)