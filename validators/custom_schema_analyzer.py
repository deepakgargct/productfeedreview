"""
Custom Schema Analyzer Module

This module analyzes custom schema markup and provides suggestions for enhancements
based on ChatGPT product schema best practices. It validates schema structure,
identifies missing recommended fields, and offers optimization recommendations.
"""

import json
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
from dataclasses import dataclass, field


class SeverityLevel(Enum):
    """Enum for issue severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SchemaIssue:
    """Represents a single schema issue found during analysis."""
    severity: SeverityLevel
    field: str
    message: str
    suggestion: str
    affected_path: Optional[str] = None


@dataclass
class SchemaAnalysisResult:
    """Contains the complete analysis results for a schema."""
    is_valid: bool
    issues: List[SchemaIssue] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    score: float = 0.0
    warnings_count: int = 0
    critical_issues_count: int = 0


class ProductSchemaAnalyzer:
    """
    Analyzes product schema markup and provides enhancement suggestions
    based on ChatGPT product schema best practices.
    """

    # Required fields for valid product schema
    REQUIRED_FIELDS = {
        "@context": "Must be 'https://schema.org'",
        "@type": "Must be 'Product'",
        "name": "Product name is required",
        "description": "Product description is required",
    }

    # Highly recommended fields for better product schema
    RECOMMENDED_FIELDS = {
        "image": "Product image URL for rich results",
        "brand": "Brand information helps with product identification",
        "offers": "Price and availability information",
        "aggregateRating": "User ratings increase trust and CTR",
        "review": "Individual product reviews with ratings",
        "sku": "Stock keeping unit for inventory tracking",
        "availability": "Current product availability status",
        "priceCurrency": "Currency specification for prices",
        "url": "Canonical URL to product page",
    }

    # Best practices for specific fields
    FIELD_VALIDATIONS = {
        "name": {"min_length": 5, "max_length": 200},
        "description": {"min_length": 20, "max_length": 5000},
        "image": {"format": "url", "min_count": 1},
        "aggregateRating": {
            "required_subfields": ["ratingValue", "ratingCount"],
            "rating_range": (1, 5),
        },
        "offers": {
            "required_subfields": ["price", "priceCurrency", "availability"],
            "valid_availability": [
                "InStock",
                "OutOfStock",
                "PreOrder",
                "Discontinued",
            ],
        },
    }

    def __init__(self):
        """Initialize the schema analyzer."""
        self.issues: List[SchemaIssue] = []
        self.suggestions: List[str] = []

    def analyze(self, schema: Dict[str, Any]) -> SchemaAnalysisResult:
        """
        Analyze a product schema for validity and provide enhancement suggestions.

        Args:
            schema: The schema dictionary to analyze

        Returns:
            SchemaAnalysisResult containing all findings
        """
        self.issues = []
        self.suggestions = []

        # Validate required fields
        self._validate_required_fields(schema)

        # Check recommended fields
        self._check_recommended_fields(schema)

        # Validate field-specific rules
        self._validate_field_specific_rules(schema)

        # Check for schema structure issues
        self._check_schema_structure(schema)

        # Generate enhancement suggestions
        self._generate_enhancements(schema)

        # Calculate score
        score = self._calculate_score(schema)

        # Create result
        critical_count = sum(
            1 for issue in self.issues if issue.severity == SeverityLevel.CRITICAL
        )
        warning_count = sum(
            1 for issue in self.issues if issue.severity == SeverityLevel.WARNING
        )

        return SchemaAnalysisResult(
            is_valid=critical_count == 0,
            issues=self.issues,
            suggestions=self.suggestions,
            score=score,
            warnings_count=warning_count,
            critical_issues_count=critical_count,
        )

    def _validate_required_fields(self, schema: Dict[str, Any]) -> None:
        """Validate that all required fields are present."""
        for field, description in self.REQUIRED_FIELDS.items():
            if field not in schema:
                self.issues.append(
                    SchemaIssue(
                        severity=SeverityLevel.CRITICAL,
                        field=field,
                        message=f"Missing required field: {field}",
                        suggestion=f"Add '{field}' field. {description}",
                    )
                )
            elif not schema[field]:
                self.issues.append(
                    SchemaIssue(
                        severity=SeverityLevel.CRITICAL,
                        field=field,
                        message=f"Required field '{field}' is empty",
                        suggestion=f"Populate '{field}' with valid content.",
                    )
                )

    def _check_recommended_fields(self, schema: Dict[str, Any]) -> None:
        """Check for presence of recommended fields."""
        missing_recommended = []
        for field, description in self.RECOMMENDED_FIELDS.items():
            if field not in schema:
                missing_recommended.append(f"- {field}: {description}")

        if missing_recommended:
            self.issues.append(
                SchemaIssue(
                    severity=SeverityLevel.WARNING,
                    field="recommended_fields",
                    message="Missing recommended fields",
                    suggestion="Consider adding: " + ", ".join(
                        [f.split(":")[0].strip() for f in missing_recommended]
                    ),
                    affected_path="root",
                )
            )

    def _validate_field_specific_rules(self, schema: Dict[str, Any]) -> None:
        """Validate field-specific constraints and best practices."""
        # Validate name field
        if "name" in schema:
            name = schema["name"]
            if isinstance(name, str):
                if len(name) < self.FIELD_VALIDATIONS["name"]["min_length"]:
                    self.issues.append(
                        SchemaIssue(
                            severity=SeverityLevel.WARNING,
                            field="name",
                            message="Product name is too short",
                            suggestion=f"Use a descriptive name with at least {self.FIELD_VALIDATIONS['name']['min_length']} characters",
                        )
                    )
                if len(name) > self.FIELD_VALIDATIONS["name"]["max_length"]:
                    self.issues.append(
                        SchemaIssue(
                            severity=SeverityLevel.WARNING,
                            field="name",
                            message="Product name is too long",
                            suggestion=f"Keep name under {self.FIELD_VALIDATIONS['name']['max_length']} characters",
                        )
                    )

        # Validate description field
        if "description" in schema:
            description = schema["description"]
            if isinstance(description, str):
                if len(description) < self.FIELD_VALIDATIONS["description"]["min_length"]:
                    self.issues.append(
                        SchemaIssue(
                            severity=SeverityLevel.WARNING,
                            field="description",
                            message="Product description is too short",
                            suggestion=f"Provide a detailed description with at least {self.FIELD_VALIDATIONS['description']['min_length']} characters",
                        )
                    )

        # Validate image field
        if "image" in schema:
            images = schema["image"] if isinstance(schema["image"], list) else [schema["image"]]
            if len(images) < self.FIELD_VALIDATIONS["image"]["min_count"]:
                self.issues.append(
                    SchemaIssue(
                        severity=SeverityLevel.WARNING,
                        field="image",
                        message="Insufficient product images",
                        suggestion="Add at least 3 high-quality product images for better engagement",
                    )
                )

        # Validate aggregateRating field
        if "aggregateRating" in schema:
            self._validate_aggregate_rating(schema["aggregateRating"])

        # Validate offers field
        if "offers" in schema:
            self._validate_offers(schema["offers"])

    def _validate_aggregate_rating(self, rating: Any) -> None:
        """Validate aggregateRating field."""
        if not isinstance(rating, dict):
            self.issues.append(
                SchemaIssue(
                    severity=SeverityLevel.WARNING,
                    field="aggregateRating",
                    message="aggregateRating should be an object",
                    suggestion="Use an object with ratingValue, ratingCount, and reviewCount",
                )
            )
            return

        required_subfields = self.FIELD_VALIDATIONS["aggregateRating"]["required_subfields"]
        for subfield in required_subfields:
            if subfield not in rating:
                self.issues.append(
                    SchemaIssue(
                        severity=SeverityLevel.WARNING,
                        field="aggregateRating",
                        message=f"Missing '{subfield}' in aggregateRating",
                        suggestion=f"Add '{subfield}' to provide complete rating information",
                        affected_path="aggregateRating",
                    )
                )

        if "ratingValue" in rating:
            try:
                value = float(rating["ratingValue"])
                min_val, max_val = self.FIELD_VALIDATIONS["aggregateRating"]["rating_range"]
                if not (min_val <= value <= max_val):
                    self.issues.append(
                        SchemaIssue(
                            severity=SeverityLevel.WARNING,
                            field="aggregateRating",
                            message=f"Rating value {value} is outside valid range",
                            suggestion=f"Use rating between {min_val} and {max_val}",
                            affected_path="aggregateRating.ratingValue",
                        )
                    )
            except (ValueError, TypeError):
                self.issues.append(
                    SchemaIssue(
                        severity=SeverityLevel.WARNING,
                        field="aggregateRating",
                        message="ratingValue should be a number",
                        suggestion="Provide numeric rating value",
                        affected_path="aggregateRating.ratingValue",
                    )
                )

    def _validate_offers(self, offers: Any) -> None:
        """Validate offers field."""
        if not isinstance(offers, (dict, list)):
            self.issues.append(
                SchemaIssue(
                    severity=SeverityLevel.WARNING,
                    field="offers",
                    message="offers should be an object or array",
                    suggestion="Structure offers with price, priceCurrency, and availability",
                )
            )
            return

        offers_list = offers if isinstance(offers, list) else [offers]

        for idx, offer in enumerate(offers_list):
            if not isinstance(offer, dict):
                continue

            required_subfields = self.FIELD_VALIDATIONS["offers"]["required_subfields"]
            for subfield in required_subfields:
                if subfield not in offer:
                    self.issues.append(
                        SchemaIssue(
                            severity=SeverityLevel.WARNING,
                            field="offers",
                            message=f"Missing '{subfield}' in offers[{idx}]",
                            suggestion=f"Add '{subfield}' for complete pricing information",
                            affected_path=f"offers[{idx}]",
                        )
                    )

            if "availability" in offer:
                valid_values = self.FIELD_VALIDATIONS["offers"]["valid_availability"]
                if offer["availability"] not in valid_values:
                    self.issues.append(
                        SchemaIssue(
                            severity=SeverityLevel.WARNING,
                            field="offers",
                            message=f"Invalid availability value: {offer['availability']}",
                            suggestion=f"Use one of: {', '.join(valid_values)}",
                            affected_path=f"offers[{idx}].availability",
                        )
                    )

    def _check_schema_structure(self, schema: Dict[str, Any]) -> None:
        """Check overall schema structure and best practices."""
        # Check if @type is correct
        if "@type" in schema and schema["@type"] != "Product":
            self.issues.append(
                SchemaIssue(
                    severity=SeverityLevel.CRITICAL,
                    field="@type",
                    message=f"Invalid @type value: {schema['@type']}",
                    suggestion="Use @type: 'Product' for product schema",
                )
            )

        # Check if @context is correct
        if "@context" in schema and schema["@context"] != "https://schema.org":
            self.issues.append(
                SchemaIssue(
                    severity=SeverityLevel.WARNING,
                    field="@context",
                    message="Non-standard @context value",
                    suggestion="Use @context: 'https://schema.org'",
                )
            )

    def _generate_enhancements(self, schema: Dict[str, Any]) -> None:
        """Generate specific enhancement suggestions."""
        suggestions = []

        # Suggest structured data enhancements
        if "review" not in schema:
            suggestions.append(
                "Add 'review' array to include individual product reviews for better SEO and user trust"
            )

        if "brand" not in schema:
            suggestions.append(
                "Include 'brand' information to help search engines understand product origin"
            )

        if "sku" not in schema:
            suggestions.append(
                "Add 'sku' field for better inventory tracking and product identification"
            )

        if "url" not in schema:
            suggestions.append(
                "Include canonical 'url' pointing to the product page for proper indexing"
            )

        # Suggest content improvements
        if "description" in schema:
            desc_len = len(str(schema["description"]))
            if desc_len < 100:
                suggestions.append(
                    "Expand product description to at least 100 characters for better SEO performance"
                )

        # Suggest offer improvements
        if "offers" in schema:
            offers = schema["offers"] if isinstance(schema["offers"], list) else [schema["offers"]]
            for offer in offers:
                if isinstance(offer, dict) and "url" not in offer:
                    suggestions.append(
                        "Add 'url' field to offers linking to the product purchase page"
                    )

        self.suggestions = suggestions

    def _calculate_score(self, schema: Dict[str, Any]) -> float:
        """
        Calculate an overall schema quality score (0-100).

        Returns:
            float: Score between 0 and 100
        """
        total_possible_points = 100
        points = 0

        # Required fields (40 points)
        required_points = 40
        missing_required = sum(
            1
            for field in self.REQUIRED_FIELDS
            if field not in schema or not schema[field]
        )
        points += (
            required_points
            * (len(self.REQUIRED_FIELDS) - missing_required)
            / len(self.REQUIRED_FIELDS)
        )

        # Recommended fields (40 points)
        recommended_points = 40
        missing_recommended = sum(
            1 for field in self.RECOMMENDED_FIELDS if field not in schema
        )
        points += (
            recommended_points
            * (len(self.RECOMMENDED_FIELDS) - missing_recommended)
            / len(self.RECOMMENDED_FIELDS)
        )

        # Issues penalty (20 points)
        issues_points = 20
        total_issues = len(self.issues)
        penalty = min(
            issues_points, total_issues * 2
        )  # 2 points per issue up to 20 points
        points += issues_points - penalty

        return round(max(0, min(100, points)), 2)

    def generate_report(
        self, schema: Dict[str, Any], include_json: bool = False
    ) -> str:
        """
        Generate a human-readable analysis report.

        Args:
            schema: The schema to analyze
            include_json: Whether to include JSON representation

        Returns:
            str: Formatted analysis report
        """
        result = self.analyze(schema)

        report = []
        report.append("=" * 70)
        report.append("PRODUCT SCHEMA ANALYSIS REPORT")
        report.append("=" * 70)
        report.append("")

        # Overall score and validity
        report.append(f"Overall Score: {result.score}/100")
        report.append(
            f"Status: {'✓ VALID' if result.is_valid else '✗ INVALID'}"
        )
        report.append(f"Critical Issues: {result.critical_issues_count}")
        report.append(f"Warnings: {result.warnings_count}")
        report.append("")

        # Issues section
        if result.issues:
            report.append("ISSUES FOUND:")
            report.append("-" * 70)
            for issue in result.issues:
                report.append(
                    f"[{issue.severity.value.upper()}] {issue.field}: {issue.message}"
                )
                report.append(f"  → Suggestion: {issue.suggestion}")
                if issue.affected_path:
                    report.append(f"  → Path: {issue.affected_path}")
                report.append("")

        # Suggestions section
        if result.suggestions:
            report.append("ENHANCEMENT SUGGESTIONS:")
            report.append("-" * 70)
            for idx, suggestion in enumerate(result.suggestions, 1):
                report.append(f"{idx}. {suggestion}")
            report.append("")

        report.append("=" * 70)

        if include_json:
            report.append("JSON REPRESENTATION:")
            report.append(json.dumps(schema, indent=2))

        return "\n".join(report)


def analyze_product_schema(schema: Dict[str, Any]) -> SchemaAnalysisResult:
    """
    Convenience function to analyze a product schema.

    Args:
        schema: The product schema to analyze

    Returns:
        SchemaAnalysisResult with analysis findings
    """
    analyzer = ProductSchemaAnalyzer()
    return analyzer.analyze(schema)
