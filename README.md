# Command for PowerShell to clear gen_py cache:

Remove-Item -Recurse -Force $env:TEMP\gen_py

# Command for running tests

python -m pytest tests/test_reference_extractor.py -v

# Generate coverage report

python -m pytest --cov=utils test_reference_extractor.py

- Local + Elements

- Log: 646
- Simplifed 615
-

Local + External

- CO2PBL55_1 to remove and treat manually

Summary

- Log: 646
- Simplifed 615
- Processed by llm: 615

{
"type": "product",
"file": "2022 - P1 Berekening Ladenkasten 794-KLEUR.xlsx",
"sheet": "OVERZICHT COP",
"cell": "I11",
"cleaned_formula": "I3+X19",
"id": "CO2PBL55_1",
"references": [
{
"type": "none",
"file": "2022 - P1 Berekening Ladenkasten 794-KLEUR.xlsx",
"sheet": "OVERZICHT COP",
"cell": "I3",
"cleaned_formula": "'CO55'!H59+'PLADE 55'!J39+FR546x394!J33",
"references": [
{
"type": "element",
"id": "CO55_52.669",
"cell": "H59"
},
{
"type": "none",
"file": "2022 - P1 Berekening Ladenkasten 794-KLEUR.xlsx",
"sheet": "PLADE 55",
"cell": "J39",
"cleaned_formula": "H39*J38",
"references": [
{
"type": "element",
"id": "PLADE 55_38.77",
"cell": "H39"
},
{
"type": "none",
"file": "2022 - P1 Berekening Ladenkasten 794-KLEUR.xlsx",
"sheet": "PLADE 55",
"cell": "J38",
"cleaned_formula": "Cellhasnoformulainfile",
"value": 2.0
}
]
},
{
"type": "none",
"file": "2022 - P1 Berekening Ladenkasten 794-KLEUR.xlsx",
"sheet": "FR546x394",
"cell": "J33",
"cleaned_formula": "H33*2",
"references": [
{
"type": "element",
"id": "FR546x394_5.754",
"cell": "H33"
}
]
}
]
},
{
"type": "none",
"file": "2022 - P1 Berekening Ladenkasten 794-KLEUR.xlsx",
"sheet": "OVERZICHT COP",
"cell": "X19",
"cleaned_formula": "'LADE 55'!H37+'LADE 55'!R37",
"references": [
{
"type": "element",
"id": "LADE 55_20.42",
"cell": "H37"
},
{
"type": "binnenlade",
"size": 55.0,
"value": 24.208,
"cell": "R37"
}
]
}
]
},
