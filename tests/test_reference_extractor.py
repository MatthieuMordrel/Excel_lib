from utils.reference_extractor import ReferenceExtractor

class TestReferenceExtractor:
    """Test cases for the ReferenceExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.extractor = ReferenceExtractor()
    
    def test_cell_validation_through_extraction(self):
        """Test cell validation indirectly through the extract_references method."""
        # Valid cells should be extracted
        formula = "A1+Z999+AA1+ZZ123"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        # Check that all valid cells were extracted
        cells = [ref["cell"] for ref in refs]
        assert "A1" in cells
        assert "Z999" in cells
        assert "AA1" in cells
        assert "ZZ123" in cells
        
        # Invalid cells should not be extracted
        formula = "AAA1+A1234+a1+1A+A+1"
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        # Check that no invalid cells were extracted
        cells = [ref["cell"] for ref in refs]
        assert "AAA1" not in cells
        assert "A1234" not in cells
        assert "a1" not in cells
        assert "1A" not in cells
        assert "A" not in cells
        assert "1" not in cells
    
    # We'll test the reference creation indirectly through extract_references
    def test_reference_creation_through_extraction(self):
        """Test reference creation indirectly through extract_references."""
        formula = "A1"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        assert len(refs) == 1
        ref = refs[0]
        assert ref["id"] == "test.xlsx_Sheet1_A1"
        assert ref["file"] == "test.xlsx"
        assert ref["sheet"] == "Sheet1"
        assert ref["cell"] == "A1"
        assert ref["formula"] is None
        assert ref["isElement"] is False
        
        # Test with spaces in sheet name
        formula = "'My Sheet'!B2"
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        assert len(refs) == 1
        ref = refs[0]
        assert ref["id"] == "test.xlsx_MySheet_B2"
    
    def test_extract_references_simple_cell(self):
        """Test extracting simple cell references."""
        formula = "A1+B2+C3"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, updated_formula = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        assert len(refs) == 3
        assert refs[0]["cell"] == "A1"
        assert refs[1]["cell"] == "B2"
        assert refs[2]["cell"] == "C3"
        
        # Check updated formula
        assert updated_formula == "test.xlsx_Sheet1_A1+test.xlsx_Sheet1_B2+test.xlsx_Sheet1_C3"
    
    def test_extract_references_two_letter_columns(self):
        """Test extracting references with two-letter columns."""
        formula = "AA1+AB2+ZZ99"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        assert len(refs) == 3
        assert refs[0]["cell"] == "AA1"
        assert refs[1]["cell"] == "AB2"
        assert refs[2]["cell"] == "ZZ99"
    
    def test_extract_references_internal_sheet(self):
        """Test extracting references to other sheets in the same file."""
        formula = "'Sheet2'!A1+Sheet3!B2"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, updated_formula = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        assert len(refs) == 2
        assert refs[0]["sheet"] == "Sheet2"
        assert refs[0]["cell"] == "A1"
        assert refs[1]["sheet"] == "Sheet3"
        assert refs[1]["cell"] == "B2"
        
        # Check updated formula
        assert "test.xlsx_Sheet2_A1" in updated_formula
        assert "test.xlsx_Sheet3_B2" in updated_formula
    
    def test_extract_references_external_file(self):
        """Test extracting references to other files."""
        formula = "'[external.xlsx]Sheet1'!A1"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, updated_formula = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        assert len(refs) == 1
        assert refs[0]["file"] == "external.xlsx"
        assert refs[0]["sheet"] == "Sheet1"
        assert refs[0]["cell"] == "A1"
        
        # Check updated formula
        assert updated_formula == "external.xlsx_Sheet1_A1"
    
    def test_extract_references_special_cases(self):
        """Test extracting references with special sheet names."""
        formula = "FRIGO+OVEN!A1+KOLOM+BL!B2+LEGGERS+OVEN!C3"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        assert len(refs) == 3
        assert refs[0]["sheet"] == "FRIGO+OVEN"
        assert refs[0]["cell"] == "A1"
        assert refs[1]["sheet"] == "KOLOM+BL"
        assert refs[1]["cell"] == "B2"
        assert refs[2]["sheet"] == "LEGGERS+OVEN"
        assert refs[2]["cell"] == "C3"
    
    def test_extract_references_sum_function(self):
        """Test extracting references within SUM function."""
        formula = "SUM(Sheet2!A1:A10)"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        # This should extract at least the first cell reference
        assert len(refs) > 0
        assert refs[0]["sheet"] == "Sheet2"
        assert refs[0]["cell"] == "A1"
    
    def test_extract_references_complex_formula(self):
        """Test extracting references from a complex formula with mixed references."""
        formula = "A1+'Sheet2'!B2+'[external.xlsx]Sheet3'!C3+SUM(Sheet4!D4:D10)"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        # Should extract at least 4 references
        assert len(refs) >= 4
        
        # Check for specific references
        cell_refs = [(ref["file"], ref["sheet"], ref["cell"]) for ref in refs]
        assert ("test.xlsx", "Sheet1", "A1") in cell_refs
        assert ("test.xlsx", "Sheet2", "B2") in cell_refs
        assert ("external.xlsx", "Sheet3", "C3") in cell_refs
        assert ("test.xlsx", "Sheet4", "D4") in cell_refs
    
    def test_no_duplicate_references(self):
        """Test that duplicate references are not extracted multiple times."""
        formula = "A1+A1+A1"  # Same cell referenced three times
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, _ = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        # Should only extract one reference
        assert len(refs) == 1
        assert refs[0]["cell"] == "A1"
        
    def test_complex_formula_with_sheet_names_containing_numbers(self):
        """Test extracting references from formulas with sheet names containing numbers."""
        formula = "'CO35'!H59+'LADE 35'!J37+FR346x196!J33+'PLADE 35'!H39+FR346x394!H33"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, updated_formula = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        # Should extract 5 references
        assert len(refs) == 5
        
        # Check for specific references
        sheet_cell_pairs = [(ref["sheet"], ref["cell"]) for ref in refs]
        assert ("CO35", "H59") in sheet_cell_pairs
        assert ("LADE 35", "J37") in sheet_cell_pairs
        assert ("FR346x196", "J33") in sheet_cell_pairs
        assert ("PLADE 35", "H39") in sheet_cell_pairs
        assert ("FR346x394", "H33") in sheet_cell_pairs
        
        # Check updated formula contains all the transformed references
        for ref in refs:
            assert f"{parent_file}_{ref['sheet']}_{ref['cell']}".replace(" ", "") in updated_formula
    
    def test_formula_with_double_letter_operator(self):
        """Test extracting references from formulas with double letter operators."""
        formula = "P3+AE19"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, updated_formula = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        # Should extract 2 references
        assert len(refs) == 2
        
        # Check for specific references
        cells = [ref["cell"] for ref in refs]
        assert "P3" in cells
        assert "AE19" in cells
        
        # Check updated formula
        assert f"{parent_file}_{parent_sheet}_P3" in updated_formula
        assert f"{parent_file}_{parent_sheet}_AE19" in updated_formula
        assert len(updated_formula) > 0  # Ensure updated formula is not empty
    
    def test_complex_external_reference_with_spaces(self):
        """Test extracting complex external references with spaces in sheet names."""
        formula = "'[2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx]OVERZICHT COP'!Y20"
        parent_file = "test.xlsx"
        parent_sheet = "Sheet1"
        
        refs, updated_formula = self.extractor.extract_references(formula, parent_file, parent_sheet)
        
        # Should extract 1 reference
        assert len(refs) == 1
        
        # Check the reference details
        ref = refs[0]
        assert ref["file"] == "2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx"
        assert ref["sheet"] == "OVERZICHT COP"
        assert ref["cell"] == "Y20"
        
        # Check updated formula
        expected_id = "2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx_OVERZICHT COP_Y20".replace(" ", "")
        assert expected_id in updated_formula
