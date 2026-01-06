"""
Priority-Based ChatGPT Schema Management System

This module provides a comprehensive schema management system with priority-based
handling for product feed review operations. It includes CRITICAL, HIGH, MEDIUM,
and LOW priority attributes with corresponding impact scores.

Author: deepakgargct
Created: 2026-01-06 13:35:12 UTC
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


class PriorityLevel(Enum):
    """Priority levels for schema attributes with impact scores"""
    CRITICAL = 4  # Impact score: 4.0
    HIGH = 3      # Impact score: 3.0
    MEDIUM = 2    # Impact score: 2.0
    LOW = 1       # Impact score: 1.0


class ImpactScore:
    """Impact score calculator for schema attributes"""
    
    IMPACT_MULTIPLIER = {
        PriorityLevel.CRITICAL: 4.0,
        PriorityLevel.HIGH: 3.0,
        PriorityLevel.MEDIUM: 2.0,
        PriorityLevel.LOW: 1.0,
    }
    
    @staticmethod
    def calculate(priority: PriorityLevel, weight: float = 1.0) -> float:
        """
        Calculate impact score based on priority level and optional weight
        
        Args:
            priority: The priority level
            weight: Optional weight multiplier (default: 1.0)
            
        Returns:
            float: Calculated impact score
        """
        base_score = ImpactScore.IMPACT_MULTIPLIER.get(priority, 1.0)
        return base_score * weight


@dataclass
class SchemaAttribute:
    """Represents a schema attribute with priority and impact information"""
    
    name: str
    description: str
    priority: PriorityLevel
    data_type: str = "string"
    required: bool = False
    weight: float = 1.0
    impact_score: float = field(init=False)
    validation_rules: List[str] = field(default_factory=list)
    examples: List[Any] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate impact score after initialization"""
        self.impact_score = ImpactScore.calculate(self.priority, self.weight)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert attribute to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority.name,
            "impact_score": self.impact_score,
            "data_type": self.data_type,
            "required": self.required,
            "weight": self.weight,
            "validation_rules": self.validation_rules,
            "examples": self.examples,
        }


@dataclass
class SchemaManager:
    """
    Priority-based schema manager for ChatGPT product feed review operations
    """
    
    schema_name: str
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    attributes: Dict[str, SchemaAttribute] = field(default_factory=dict)
    description: str = ""
    
    def add_critical_attribute(
        self,
        name: str,
        description: str,
        data_type: str = "string",
        required: bool = True,
        weight: float = 1.0,
        validation_rules: Optional[List[str]] = None,
        examples: Optional[List[Any]] = None,
    ) -> SchemaAttribute:
        """Add a CRITICAL priority attribute to the schema"""
        attr = SchemaAttribute(
            name=name,
            description=description,
            priority=PriorityLevel.CRITICAL,
            data_type=data_type,
            required=required,
            weight=weight,
            validation_rules=validation_rules or [],
            examples=examples or [],
        )
        self.attributes[name] = attr
        return attr
    
    def add_high_attribute(
        self,
        name: str,
        description: str,
        data_type: str = "string",
        required: bool = True,
        weight: float = 1.0,
        validation_rules: Optional[List[str]] = None,
        examples: Optional[List[Any]] = None,
    ) -> SchemaAttribute:
        """Add a HIGH priority attribute to the schema"""
        attr = SchemaAttribute(
            name=name,
            description=description,
            priority=PriorityLevel.HIGH,
            data_type=data_type,
            required=required,
            weight=weight,
            validation_rules=validation_rules or [],
            examples=examples or [],
        )
        self.attributes[name] = attr
        return attr
    
    def add_medium_attribute(
        self,
        name: str,
        description: str,
        data_type: str = "string",
        required: bool = False,
        weight: float = 1.0,
        validation_rules: Optional[List[str]] = None,
        examples: Optional[List[Any]] = None,
    ) -> SchemaAttribute:
        """Add a MEDIUM priority attribute to the schema"""
        attr = SchemaAttribute(
            name=name,
            description=description,
            priority=PriorityLevel.MEDIUM,
            data_type=data_type,
            required=required,
            weight=weight,
            validation_rules=validation_rules or [],
            examples=examples or [],
        )
        self.attributes[name] = attr
        return attr
    
    def add_low_attribute(
        self,
        name: str,
        description: str,
        data_type: str = "string",
        required: bool = False,
        weight: float = 1.0,
        validation_rules: Optional[List[str]] = None,
        examples: Optional[List[Any]] = None,
    ) -> SchemaAttribute:
        """Add a LOW priority attribute to the schema"""
        attr = SchemaAttribute(
            name=name,
            description=description,
            priority=PriorityLevel.LOW,
            data_type=data_type,
            required=required,
            weight=weight,
            validation_rules=validation_rules or [],
            examples=examples or [],
        )
        self.attributes[name] = attr
        return attr
    
    def get_attributes_by_priority(
        self, priority: PriorityLevel
    ) -> List[SchemaAttribute]:
        """Get all attributes filtered by priority level"""
        return [
            attr for attr in self.attributes.values()
            if attr.priority == priority
        ]
    
    def get_critical_attributes(self) -> List[SchemaAttribute]:
        """Get all CRITICAL priority attributes"""
        return self.get_attributes_by_priority(PriorityLevel.CRITICAL)
    
    def get_high_attributes(self) -> List[SchemaAttribute]:
        """Get all HIGH priority attributes"""
        return self.get_attributes_by_priority(PriorityLevel.HIGH)
    
    def get_medium_attributes(self) -> List[SchemaAttribute]:
        """Get all MEDIUM priority attributes"""
        return self.get_attributes_by_priority(PriorityLevel.MEDIUM)
    
    def get_low_attributes(self) -> List[SchemaAttribute]:
        """Get all LOW priority attributes"""
        return self.get_attributes_by_priority(PriorityLevel.LOW)
    
    def get_required_attributes(self) -> List[SchemaAttribute]:
        """Get all required attributes"""
        return [attr for attr in self.attributes.values() if attr.required]
    
    def calculate_overall_impact_score(self) -> float:
        """Calculate the overall impact score for the entire schema"""
        if not self.attributes:
            return 0.0
        return sum(attr.impact_score for attr in self.attributes.values())
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the schema"""
        return {
            "schema_name": self.schema_name,
            "version": self.version,
            "created_at": self.created_at,
            "description": self.description,
            "total_attributes": len(self.attributes),
            "critical_count": len(self.get_critical_attributes()),
            "high_count": len(self.get_high_attributes()),
            "medium_count": len(self.get_medium_attributes()),
            "low_count": len(self.get_low_attributes()),
            "required_count": len(self.get_required_attributes()),
            "overall_impact_score": self.calculate_overall_impact_score(),
            "attributes": {
                name: attr.to_dict() for name, attr in self.attributes.items()
            },
        }
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate data against the schema
        
        Args:
            data: Dictionary of data to validate
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Check for required attributes
        for attr in self.get_required_attributes():
            if attr.name not in data:
                errors.append(
                    f"Required attribute '{attr.name}' (Priority: {attr.priority.name}) is missing"
                )
        
        # Check for unexpected attributes
        for key in data.keys():
            if key not in self.attributes:
                errors.append(f"Unexpected attribute '{key}'")
        
        return len(errors) == 0, errors
    
    def sort_attributes_by_impact(self, descending: bool = True) -> List[SchemaAttribute]:
        """
        Sort attributes by impact score
        
        Args:
            descending: If True, sort from highest to lowest impact
            
        Returns:
            List of sorted attributes
        """
        return sorted(
            self.attributes.values(),
            key=lambda attr: attr.impact_score,
            reverse=descending,
        )


class ProductFeedSchema(SchemaManager):
    """
    Specialized schema manager for product feed review operations
    Inherits from SchemaManager with pre-configured product feed attributes
    """
    
    def __init__(self):
        super().__init__(
            schema_name="ProductFeedSchema",
            version="1.0.0",
            description="Schema for ChatGPT-based product feed review and validation",
        )
        self._initialize_product_feed_attributes()
    
    def _initialize_product_feed_attributes(self):
        """Initialize standard product feed attributes with priorities"""
        
        # CRITICAL attributes
        self.add_critical_attribute(
            name="product_id",
            description="Unique identifier for the product",
            data_type="string",
            required=True,
            validation_rules=["not_empty", "unique"],
            examples=["PROD-12345", "SKU-67890"],
        )
        
        self.add_critical_attribute(
            name="product_name",
            description="Name of the product",
            data_type="string",
            required=True,
            validation_rules=["not_empty", "max_length:255"],
            examples=["Wireless Bluetooth Headphones", "USB-C Cable"],
        )
        
        self.add_critical_attribute(
            name="price",
            description="Product price",
            data_type="float",
            required=True,
            validation_rules=["not_null", "positive"],
            examples=[29.99, 99.99],
        )
        
        # HIGH attributes
        self.add_high_attribute(
            name="category",
            description="Product category classification",
            data_type="string",
            required=True,
            validation_rules=["not_empty"],
            examples=["Electronics", "Accessories"],
        )
        
        self.add_high_attribute(
            name="description",
            description="Detailed product description",
            data_type="string",
            required=True,
            validation_rules=["min_length:50", "max_length:2000"],
            examples=["High-quality wireless headphones with noise cancellation..."],
        )
        
        self.add_high_attribute(
            name="availability",
            description="Stock availability status",
            data_type="string",
            required=True,
            validation_rules=["in_list:in_stock,out_of_stock,pre_order"],
            examples=["in_stock", "out_of_stock"],
        )
        
        # MEDIUM attributes
        self.add_medium_attribute(
            name="rating",
            description="Product rating (0-5 stars)",
            data_type="float",
            required=False,
            weight=1.5,
            validation_rules=["min:0", "max:5"],
            examples=[4.5, 3.8],
        )
        
        self.add_medium_attribute(
            name="review_count",
            description="Number of customer reviews",
            data_type="integer",
            required=False,
            validation_rules=["non_negative"],
            examples=[150, 2340],
        )
        
        self.add_medium_attribute(
            name="manufacturer",
            description="Product manufacturer name",
            data_type="string",
            required=False,
            validation_rules=["max_length:255"],
            examples=["Sony", "Apple"],
        )
        
        # LOW attributes
        self.add_low_attribute(
            name="color",
            description="Product color variant",
            data_type="string",
            required=False,
            examples=["Black", "Silver", "White"],
        )
        
        self.add_low_attribute(
            name="size",
            description="Product size specification",
            data_type="string",
            required=False,
            examples=["M", "L", "10cm x 5cm"],
        )
        
        self.add_low_attribute(
            name="sku",
            description="Stock keeping unit",
            data_type="string",
            required=False,
            examples=["SKU-12345"],
        )


def main():
    """Example usage of the schema manager"""
    
    # Create a product feed schema
    schema = ProductFeedSchema()
    
    # Print schema summary
    print("=" * 80)
    print("PRODUCT FEED SCHEMA SUMMARY")
    print("=" * 80)
    summary = schema.get_schema_summary()
    
    print(f"\nSchema: {summary['schema_name']} v{summary['version']}")
    print(f"Description: {summary['description']}")
    print(f"Created: {summary['created_at']}")
    print(f"\nAttribute Counts:")
    print(f"  CRITICAL: {summary['critical_count']}")
    print(f"  HIGH: {summary['high_count']}")
    print(f"  MEDIUM: {summary['medium_count']}")
    print(f"  LOW: {summary['low_count']}")
    print(f"  Required: {summary['required_count']}")
    print(f"\nOverall Impact Score: {summary['overall_impact_score']}")
    
    # Show attributes sorted by impact
    print("\n" + "=" * 80)
    print("ATTRIBUTES SORTED BY IMPACT SCORE (Highest to Lowest)")
    print("=" * 80)
    for attr in schema.sort_attributes_by_impact(descending=True):
        print(f"\n{attr.name}")
        print(f"  Priority: {attr.priority.name}")
        print(f"  Impact Score: {attr.impact_score}")
        print(f"  Required: {attr.required}")
        print(f"  Description: {attr.description}")
    
    # Example validation
    print("\n" + "=" * 80)
    print("VALIDATION EXAMPLE")
    print("=" * 80)
    
    valid_data = {
        "product_id": "PROD-001",
        "product_name": "Wireless Headphones",
        "price": 99.99,
        "category": "Electronics",
        "description": "High-quality wireless headphones with active noise cancellation and 30-hour battery life.",
        "availability": "in_stock",
        "rating": 4.5,
        "review_count": 250,
    }
    
    is_valid, errors = schema.validate_data(valid_data)
    print(f"\nValid Data: {is_valid}")
    if errors:
        print("Errors:", errors)
    
    invalid_data = {
        "product_id": "PROD-002",
        "product_name": "USB Cable",
        # Missing required: price, category, description, availability
    }
    
    is_valid, errors = schema.validate_data(invalid_data)
    print(f"\nInvalid Data: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
