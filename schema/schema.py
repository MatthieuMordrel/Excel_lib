from typing import TypedDict, List, Literal, Optional

class ElementID(TypedDict):
    elementID: str
    quantity: int

class ProductRelationships(TypedDict):
    productElement: List[ElementID]
    productBaseMaterial: List[str]

class ProductProduct(TypedDict):
    productID: str
    relationships: ProductRelationships

class RelationshipDict(TypedDict):
    productProduct: List[ProductProduct]
    productBaseMaterial: List[str]
    productElement: List[ElementID]

class Relationship(TypedDict):
    productID: str
    relationships: RelationshipDict

class ProductSummary(TypedDict):
    products: List[Relationship]

class Reference(TypedDict):
    productID: str
    isProduct: bool
    isElement: bool
    isBaseMaterial: bool
    sheet: str
    cell: str
    value: float
    quantity: int
    references: List['Reference']

class LogEntry(TypedDict):
    productID: str
    references: List[Reference]

class FormulaResult(TypedDict):
    id: str
    file: str
    sheet: str
    cell: str
    formula: Optional[str]
    cleaned_formula: Optional[str]
    updated_formula: Optional[str]
    value: Optional[float]
    path: Optional[str]
    productID: Optional[str]
    isProduct: bool
    isElement: bool
    isBaseMaterial: bool
    isMultiplication: bool
    isDivision: bool
    hReferenceCount: int
    error: Optional[str]
    references: List['FormulaResult']

class FormulaInfo(TypedDict):
    hReferenceCount: int
    isElement: bool
    isBaseMaterial: bool
    isProduct: bool
    updated_formula: Optional[str]
    references: List[FormulaResult]

# Add types for LLM processing
class LLMProcessedProduct(TypedDict):
    type: Literal["product"]
    file: str
    sheet: str
    cell: str
    cleaned_formula: str
    id: str
    quantity: int
    references: List['LLMProcessedReference'] 

class LLMProcessedReference(TypedDict):
    type: Literal["element", "product", "base_material"]
    id: str
    quantity: int

