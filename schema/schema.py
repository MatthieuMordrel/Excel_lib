from typing import TypedDict, List

class ElementID(TypedDict):
    elementID: str

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
    references: List['Reference']

class LogEntry(TypedDict):
    productID: str
    references: List[Reference]

class FormulaResult(TypedDict):
    id: str
    file: str
    sheet: str
    cell: str
    formula: str | None
    cleaned_formula: str | None
    value: float | None
    path: str | None
    productID: str | None
    isProduct: bool
    isElement: bool
    isBaseMaterial: bool
    isMultiplication: bool
    isDivision: bool
    hReferenceCount: int
    error: str | None
    references: List['FormulaResult']

class FormulaInfo(TypedDict):
    hReferenceCount: int
    isElement: bool
    isBaseMaterial: bool
    isProduct: bool
    references: List[FormulaResult]
