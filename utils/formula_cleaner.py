import re

class FormulaCleaner:
    """Handles cleaning of Excel formulas."""

    
    # List of known folders
    FOLDERS = [
        "1- 2022-COMFORTLINE - KLEUR - MELAMINE A+ MDF BRUT + CORPUS KLEUR",
        "2 - 2022-COMFORTLINE - KLEUR - MELAMINE B + MDF BRUT + CORPUS KLEUR",
        "3 - 2022- COMFORTLINE - LAMINAAT A + CORPUS KLEUR",
        "4 - 2022- COMFORTLINE - LAMINAAT B + CORPUS KLEUR",
        "5 -2022- COMFORTLINE - POEDERLAK-5DUN FINEER + CORPUS KLEUR",
        "6 -2022- COMFORTLINE - VLAK LAK  + CORPUS KLEUR",
        "7 -2022- COMFORTLINE - LAK GEGROEFD OF KADER +FINEER   + CORPUS KLEUR",
        "8 -2022- COMFORTLINE - BALKENEIK  + CORPUS KLEUR",
        "9 -2022- COMFORTLINE - MASSIEF KADER-FINEER  + CORPUS KLEUR",
        "10 -2022- COMFORTLINE - DIK FINEER EN HOOGGLANS  + CORPUS KLEUR"
    ]
    
    @staticmethod
    def clean_formula(formula: str) -> str:
        """
        Cleans an Excel formula by removing unnecessary parts.
        
        Args:
            formula (str): The raw Excel formula
            
        Returns:
            str: The cleaned formula
        """
        if not formula:  # Just check for empty string
            return formula
        
        # Remove $ signs, single quotes, and handle "=+" pattern
        cleaned_formula = formula.replace('$', '').replace("=+", "").replace("=", "")
        
        # Remove the base URL
        base_urls = [
            "https://mordrel-my.sharepoint.com/Kovera/BASISMATERIALEN/",
            "https://mordrel-my.sharepoint.com/personal/matthieu_mordrel_pro/Documents/Work/Projects/Kovera/Project 2/BASISMATERIALEN/",
            "\\\\LS420D340\\Zaak\\Kovera\\BASISMATERIALEN\\"
        ]
        for base_url in base_urls:
            cleaned_formula = cleaned_formula.replace(base_url, "")

        
        # Remove known folders
        for folder in FormulaCleaner.FOLDERS:
            cleaned_formula = cleaned_formula.replace(f"{folder}/", "")
        
        # Remove spaces not within single quotes
        cleaned_formula = re.sub(r"(?:'[^']*')|\s+", lambda m: m.group(0) if m.group(0).startswith("'") else '', cleaned_formula)
        
        return cleaned_formula 