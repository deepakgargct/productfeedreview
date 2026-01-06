"""
Compliance Scoring Module for Product Feed Review

This module provides comprehensive compliance scoring logic that evaluates products
against ChatGPT specifications, calculates compliance percentages, identifies critical
vs warning issues, and generates actionable recommendations.

Author: deepakgargct
Date: 2026-01-06
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod
import json
from datetime import datetime


class SeverityLevel(Enum):
    """Severity levels for compliance issues"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ComplianceCategory(Enum):
    """Categories of compliance checks"""
    PRODUCT_INFORMATION = "product_information"
    CONTENT_QUALITY = "content_quality"
    SPECIFICATIONS = "specifications"
    PRICING = "pricing"
    INVENTORY = "inventory"
    IMAGES = "images"
    POLICIES = "policies"
    METADATA = "metadata"


@dataclass
class ComplianceIssue:
    """Represents a single compliance issue"""
    issue_id: str
    category: ComplianceCategory
    severity: SeverityLevel
    title: str
    description: str
    affected_field: str
    current_value: Optional[str] = None
    expected_value: Optional[str] = None
    recommendation: str = ""
    weight: float = 1.0  # Impact weight for scoring


@dataclass
class ComplianceScore:
    """Complete compliance score report"""
    product_id: str
    product_name: str
    overall_score: float  # 0-100
    compliance_percentage: float  # 0-100
    total_issues: int
    critical_issues: int
    warning_issues: int
    info_issues: int
    issues: List[ComplianceIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    category_scores: Dict[str, float] = field(default_factory=dict)
    passing: bool = False
    generated_at: str = ""
    

class ComplianceValidator(ABC):
    """Abstract base class for compliance validators"""
    
    @abstractmethod
    def validate(self, product_data: Dict[str, Any]) -> List[ComplianceIssue]:
        """Validate product data and return list of issues"""
        pass
    
    @abstractmethod
    def get_category(self) -> ComplianceCategory:
        """Return the category this validator handles"""
        pass


class ProductInformationValidator(ComplianceValidator):
    """Validates product information completeness and accuracy"""
    
    def get_category(self) -> ComplianceCategory:
        return ComplianceCategory.PRODUCT_INFORMATION
    
    def validate(self, product_data: Dict[str, Any]) -> List[ComplianceIssue]:
        issues = []
        
        # Check product title
        if not product_data.get("title"):
            issues.append(ComplianceIssue(
                issue_id="PI001",
                category=self.get_category(),
                severity=SeverityLevel.CRITICAL,
                title="Missing Product Title",
                description="Product title is required for catalog listing",
                affected_field="title",
                recommendation="Add a clear, descriptive product title (50-80 characters)",
                weight=2.0
            ))
        elif len(product_data.get("title", "")) < 20:
            issues.append(ComplianceIssue(
                issue_id="PI002",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Product Title Too Short",
                description="Product title should be descriptive and informative",
                affected_field="title",
                current_value=product_data.get("title"),
                expected_value="Minimum 20 characters",
                recommendation="Expand title to include key product attributes",
                weight=1.5
            ))
        
        # Check product SKU
        if not product_data.get("sku"):
            issues.append(ComplianceIssue(
                issue_id="PI003",
                category=self.get_category(),
                severity=SeverityLevel.CRITICAL,
                title="Missing Product SKU",
                description="SKU is required for inventory tracking",
                affected_field="sku",
                recommendation="Add a unique Stock Keeping Unit identifier",
                weight=2.0
            ))
        
        # Check product description
        if not product_data.get("description"):
            issues.append(ComplianceIssue(
                issue_id="PI004",
                category=self.get_category(),
                severity=SeverityLevel.CRITICAL,
                title="Missing Product Description",
                description="Detailed description is essential for customer understanding",
                affected_field="description",
                recommendation="Provide comprehensive product description (100-500 words)",
                weight=2.0
            ))
        elif len(product_data.get("description", "")) < 100:
            issues.append(ComplianceIssue(
                issue_id="PI005",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Product Description Too Brief",
                description="Description lacks sufficient detail",
                affected_field="description",
                current_value=f"{len(product_data.get('description', ''))} characters",
                expected_value="Minimum 100 characters",
                recommendation="Expand description to include key features, benefits, and usage",
                weight=1.5
            ))
        
        # Check product category
        if not product_data.get("category"):
            issues.append(ComplianceIssue(
                issue_id="PI006",
                category=self.get_category(),
                severity=SeverityLevel.CRITICAL,
                title="Missing Product Category",
                description="Product must be assigned to a valid category",
                affected_field="category",
                recommendation="Select appropriate product category from catalog",
                weight=1.5
            ))
        
        return issues


class ContentQualityValidator(ComplianceValidator):
    """Validates content quality standards"""
    
    def get_category(self) -> ComplianceCategory:
        return ComplianceCategory.CONTENT_QUALITY
    
    def validate(self, product_data: Dict[str, Any]) -> List[ComplianceIssue]:
        issues = []
        
        # Check for special characters or formatting issues
        title = product_data.get("title", "")
        if any(char in title for char in ["<", ">", "{", "}", "[", "]"]):
            issues.append(ComplianceIssue(
                issue_id="CQ001",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Invalid Characters in Title",
                description="Title contains special HTML or script-like characters",
                affected_field="title",
                current_value=title,
                recommendation="Remove special characters from product title",
                weight=1.0
            ))
        
        # Check for all caps
        if title and title.isupper() and len(title) > 5:
            issues.append(ComplianceIssue(
                issue_id="CQ002",
                category=self.get_category(),
                severity=SeverityLevel.INFO,
                title="Title in All Capitals",
                description="Product title is in all uppercase letters",
                affected_field="title",
                current_value=title,
                recommendation="Use proper capitalization for better readability",
                weight=0.5
            ))
        
        # Check for excessive punctuation
        description = product_data.get("description", "")
        punctuation_count = sum(1 for char in description if char in "!?.")
        if punctuation_count > len(description) / 20:  # More than 5% punctuation
            issues.append(ComplianceIssue(
                issue_id="CQ003",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Excessive Punctuation",
                description="Description contains excessive punctuation marks",
                affected_field="description",
                recommendation="Reduce punctuation and use proper sentence structure",
                weight=0.8
            ))
        
        # Check for minimum word count
        word_count = len(description.split()) if description else 0
        if word_count < 20 and description:
            issues.append(ComplianceIssue(
                issue_id="CQ004",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Insufficient Description Length",
                description="Description has too few words for adequate product information",
                affected_field="description",
                current_value=f"{word_count} words",
                expected_value="Minimum 20 words",
                recommendation="Expand description with more detailed information",
                weight=1.2
            ))
        
        return issues


class SpecificationsValidator(ComplianceValidator):
    """Validates product specifications against ChatGPT standards"""
    
    def get_category(self) -> ComplianceCategory:
        return ComplianceCategory.SPECIFICATIONS
    
    def validate(self, product_data: Dict[str, Any]) -> List[ComplianceIssue]:
        issues = []
        
        # Check for essential specifications
        specs = product_data.get("specifications", {})
        
        required_specs = ["brand", "model", "color", "size", "material"]
        for spec in required_specs:
            if spec not in specs or not specs[spec]:
                issues.append(ComplianceIssue(
                    issue_id=f"SPEC{required_specs.index(spec):03d}",
                    category=self.get_category(),
                    severity=SeverityLevel.WARNING,
                    title=f"Missing {spec.title()} Specification",
                    description=f"{spec.title()} is an important product attribute",
                    affected_field=f"specifications.{spec}",
                    recommendation=f"Add {spec} specification for complete product information",
                    weight=1.0
                ))
        
        # Validate specification values
        if specs.get("weight") and not isinstance(specs.get("weight"), (int, float)):
            issues.append(ComplianceIssue(
                issue_id="SPEC100",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Invalid Weight Format",
                description="Weight must be a numeric value",
                affected_field="specifications.weight",
                current_value=str(specs.get("weight")),
                expected_value="Numeric value with unit (e.g., 500g, 2kg)",
                recommendation="Enter weight as a number with appropriate unit",
                weight=1.0
            ))
        
        return issues


class PricingValidator(ComplianceValidator):
    """Validates pricing information"""
    
    def get_category(self) -> ComplianceCategory:
        return ComplianceCategory.PRICING
    
    def validate(self, product_data: Dict[str, Any]) -> List[ComplianceIssue]:
        issues = []
        
        # Check for price
        price = product_data.get("price")
        if not price:
            issues.append(ComplianceIssue(
                issue_id="PRICE001",
                category=self.get_category(),
                severity=SeverityLevel.CRITICAL,
                title="Missing Product Price",
                description="Product price is required for sales",
                affected_field="price",
                recommendation="Set a valid product price",
                weight=2.0
            ))
        elif isinstance(price, (int, float)):
            if price <= 0:
                issues.append(ComplianceIssue(
                    issue_id="PRICE002",
                    category=self.get_category(),
                    severity=SeverityLevel.CRITICAL,
                    title="Invalid Price Value",
                    description="Price must be greater than zero",
                    affected_field="price",
                    current_value=str(price),
                    expected_value="Price > 0",
                    recommendation="Enter a positive price value",
                    weight=2.0
                ))
        
        # Check currency
        if not product_data.get("currency"):
            issues.append(ComplianceIssue(
                issue_id="PRICE003",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Missing Currency Information",
                description="Currency must be specified with price",
                affected_field="currency",
                recommendation="Specify currency (e.g., USD, EUR, GBP)",
                weight=1.5
            ))
        
        return issues


class InventoryValidator(ComplianceValidator):
    """Validates inventory information"""
    
    def get_category(self) -> ComplianceCategory:
        return ComplianceCategory.INVENTORY
    
    def validate(self, product_data: Dict[str, Any]) -> List[ComplianceIssue]:
        issues = []
        
        stock = product_data.get("stock_quantity")
        if stock is None:
            issues.append(ComplianceIssue(
                issue_id="INV001",
                category=self.get_category(),
                severity=SeverityLevel.CRITICAL,
                title="Missing Stock Quantity",
                description="Stock quantity must be defined",
                affected_field="stock_quantity",
                recommendation="Enter current stock quantity",
                weight=1.5
            ))
        elif isinstance(stock, (int, float)) and stock < 0:
            issues.append(ComplianceIssue(
                issue_id="INV002",
                category=self.get_category(),
                severity=SeverityLevel.CRITICAL,
                title="Negative Stock Quantity",
                description="Stock quantity cannot be negative",
                affected_field="stock_quantity",
                current_value=str(stock),
                recommendation="Correct stock quantity to a non-negative value",
                weight=2.0
            ))
        
        return issues


class ImageValidator(ComplianceValidator):
    """Validates product images"""
    
    def get_category(self) -> ComplianceCategory:
        return ComplianceCategory.IMAGES
    
    def validate(self, product_data: Dict[str, Any]) -> List[ComplianceIssue]:
        issues = []
        
        images = product_data.get("images", [])
        
        if not images:
            issues.append(ComplianceIssue(
                issue_id="IMG001",
                category=self.get_category(),
                severity=SeverityLevel.CRITICAL,
                title="Missing Product Images",
                description="At least one product image is required",
                affected_field="images",
                recommendation="Upload at least 3-5 high-quality product images",
                weight=2.0
            ))
        elif len(images) < 3:
            issues.append(ComplianceIssue(
                issue_id="IMG002",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Insufficient Number of Images",
                description="Multiple images provide better product visibility",
                affected_field="images",
                current_value=f"{len(images)} image(s)",
                expected_value="Minimum 3 images",
                recommendation="Add more product images from different angles",
                weight=1.5
            ))
        
        return issues


class MetadataValidator(ComplianceValidator):
    """Validates product metadata and SEO compliance"""
    
    def get_category(self) -> ComplianceCategory:
        return ComplianceCategory.METADATA
    
    def validate(self, product_data: Dict[str, Any]) -> List[ComplianceIssue]:
        issues = []
        
        # Check meta description
        if not product_data.get("meta_description"):
            issues.append(ComplianceIssue(
                issue_id="META001",
                category=self.get_category(),
                severity=SeverityLevel.WARNING,
                title="Missing Meta Description",
                description="Meta description improves search engine visibility",
                affected_field="meta_description",
                recommendation="Add meta description (150-160 characters)",
                weight=1.0
            ))
        
        # Check meta keywords
        if not product_data.get("meta_keywords"):
            issues.append(ComplianceIssue(
                issue_id="META002",
                category=self.get_category(),
                severity=SeverityLevel.INFO,
                title="Missing Meta Keywords",
                description="Meta keywords can help with search optimization",
                affected_field="meta_keywords",
                recommendation="Add relevant keywords (5-10) separated by commas",
                weight=0.7
            ))
        
        return issues


class ComplianceScorer:
    """Main compliance scoring engine"""
    
    def __init__(self):
        """Initialize the compliance scorer with all validators"""
        self.validators: List[ComplianceValidator] = [
            ProductInformationValidator(),
            ContentQualityValidator(),
            SpecificationsValidator(),
            PricingValidator(),
            InventoryValidator(),
            ImageValidator(),
            MetadataValidator(),
        ]
        
        # Define passing thresholds
        self.critical_threshold = 0  # No critical issues allowed to pass
        self.warning_threshold = 5   # Max 5 warnings to pass
        self.compliance_threshold = 85.0  # Min 85% compliance to pass
    
    def score_product(self, product_data: Dict[str, Any]) -> ComplianceScore:
        """
        Score a product against all compliance validators.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            ComplianceScore object with detailed scoring information
        """
        product_id = product_data.get("id", "unknown")
        product_name = product_data.get("title", "Unknown Product")
        
        all_issues: List[ComplianceIssue] = []
        category_issues: Dict[str, List[ComplianceIssue]] = {}
        
        # Run all validators
        for validator in self.validators:
            issues = validator.validate(product_data)
            all_issues.extend(issues)
            category = validator.get_category().value
            category_issues[category] = issues
        
        # Separate issues by severity
        critical_issues = [i for i in all_issues if i.severity == SeverityLevel.CRITICAL]
        warning_issues = [i for i in all_issues if i.severity == SeverityLevel.WARNING]
        info_issues = [i for i in all_issues if i.severity == SeverityLevel.INFO]
        
        # Calculate compliance score
        overall_score, compliance_percentage = self._calculate_score(all_issues)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues)
        
        # Calculate category scores
        category_scores = self._calculate_category_scores(category_issues)
        
        # Determine if product passes compliance
        passing = (
            len(critical_issues) == 0 and
            len(warning_issues) <= self.warning_threshold and
            compliance_percentage >= self.compliance_threshold
        )
        
        return ComplianceScore(
            product_id=str(product_id),
            product_name=product_name,
            overall_score=overall_score,
            compliance_percentage=compliance_percentage,
            total_issues=len(all_issues),
            critical_issues=len(critical_issues),
            warning_issues=len(warning_issues),
            info_issues=len(info_issues),
            issues=all_issues,
            recommendations=recommendations,
            category_scores=category_scores,
            passing=passing,
            generated_at=datetime.utcnow().isoformat()
        )
    
    def _calculate_score(self, issues: List[ComplianceIssue]) -> Tuple[float, float]:
        """
        Calculate compliance score and percentage.
        
        Args:
            issues: List of compliance issues
            
        Returns:
            Tuple of (overall_score, compliance_percentage)
        """
        if not issues:
            return 100.0, 100.0
        
        # Weight-based scoring
        total_weight = 0.0
        deduction = 0.0
        
        for issue in issues:
            total_weight += issue.weight
            
            if issue.severity == SeverityLevel.CRITICAL:
                deduction += issue.weight * 10  # Critical: 10 points per weight
            elif issue.severity == SeverityLevel.WARNING:
                deduction += issue.weight * 5   # Warning: 5 points per weight
            elif issue.severity == SeverityLevel.INFO:
                deduction += issue.weight * 1   # Info: 1 point per weight
        
        # Calculate percentage (max deduction of 100)
        overall_score = max(0, 100 - min(deduction, 100))
        compliance_percentage = overall_score
        
        return overall_score, compliance_percentage
    
    def _generate_recommendations(self, issues: List[ComplianceIssue]) -> List[str]:
        """Generate actionable recommendations from issues"""
        recommendations = []
        
        # Prioritize by severity
        critical_recs = [i.recommendation for i in issues 
                        if i.severity == SeverityLevel.CRITICAL and i.recommendation]
        warning_recs = [i.recommendation for i in issues 
                       if i.severity == SeverityLevel.WARNING and i.recommendation]
        
        # Add critical recommendations first
        recommendations.extend(critical_recs[:5])
        recommendations.extend(warning_recs[:5])
        
        # Add summary recommendations
        if len(issues) == 0:
            recommendations.append("Excellent compliance! Product meets all requirements.")
        elif len(critical_recs) > 0:
            recommendations.append("PRIORITY: Address all critical issues before listing product.")
        elif len(warning_recs) > 0:
            recommendations.append("Review and address warning issues to improve product visibility.")
        
        return list(dict.fromkeys(recommendations))  # Remove duplicates while preserving order
    
    def _calculate_category_scores(self, 
                                  category_issues: Dict[str, List[ComplianceIssue]]
                                  ) -> Dict[str, float]:
        """Calculate compliance score for each category"""
        category_scores = {}
        
        for category, issues in category_issues.items():
            if not issues:
                category_scores[category] = 100.0
            else:
                deduction = sum(
                    issue.weight * (10 if issue.severity == SeverityLevel.CRITICAL else 
                                   5 if issue.severity == SeverityLevel.WARNING else 1)
                    for issue in issues
                )
                category_scores[category] = max(0, 100 - min(deduction, 100))
        
        return category_scores
    
    def batch_score_products(self, 
                            products: List[Dict[str, Any]]) -> List[ComplianceScore]:
        """
        Score multiple products.
        
        Args:
            products: List of product data dictionaries
            
        Returns:
            List of ComplianceScore objects
        """
        return [self.score_product(product) for product in products]
    
    def export_report(self, score: ComplianceScore, format: str = "json") -> str:
        """
        Export compliance score report in specified format.
        
        Args:
            score: ComplianceScore object
            format: Export format ('json' or 'text')
            
        Returns:
            Formatted report string
        """
        if format == "json":
            return self._export_json(score)
        elif format == "text":
            return self._export_text(score)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, score: ComplianceScore) -> str:
        """Export report as JSON"""
        report = {
            "product_id": score.product_id,
            "product_name": score.product_name,
            "overall_score": round(score.overall_score, 2),
            "compliance_percentage": round(score.compliance_percentage, 2),
            "passing": score.passing,
            "generated_at": score.generated_at,
            "summary": {
                "total_issues": score.total_issues,
                "critical_issues": score.critical_issues,
                "warning_issues": score.warning_issues,
                "info_issues": score.info_issues,
            },
            "category_scores": {k: round(v, 2) for k, v in score.category_scores.items()},
            "issues": [
                {
                    "issue_id": issue.issue_id,
                    "category": issue.category.value,
                    "severity": issue.severity.value,
                    "title": issue.title,
                    "description": issue.description,
                    "affected_field": issue.affected_field,
                    "current_value": issue.current_value,
                    "expected_value": issue.expected_value,
                    "recommendation": issue.recommendation,
                }
                for issue in score.issues
            ],
            "recommendations": score.recommendations,
        }
        return json.dumps(report, indent=2)
    
    def _export_text(self, score: ComplianceScore) -> str:
        """Export report as formatted text"""
        lines = [
            "=" * 80,
            "PRODUCT COMPLIANCE SCORE REPORT",
            "=" * 80,
            f"\nProduct ID: {score.product_id}",
            f"Product Name: {score.product_name}",
            f"Generated: {score.generated_at}",
            f"\nStatus: {'✓ PASSING' if score.passing else '✗ NEEDS IMPROVEMENT'}",
            f"Overall Score: {score.overall_score:.1f}/100",
            f"Compliance: {score.compliance_percentage:.1f}%",
            f"\nIssue Summary:",
            f"  Total Issues: {score.total_issues}",
            f"  Critical: {score.critical_issues}",
            f"  Warnings: {score.warning_issues}",
            f"  Info: {score.info_issues}",
            f"\nCategory Scores:",
        ]
        
        for category, score_value in sorted(score.category_scores.items()):
            lines.append(f"  {category.replace('_', ' ').title()}: {score_value:.1f}%")
        
        if score.issues:
            lines.extend([
                f"\nDetailed Issues:",
                "-" * 80,
            ])
            
            for issue in sorted(score.issues, 
                               key=lambda x: (x.severity != SeverityLevel.CRITICAL,
                                            x.severity != SeverityLevel.WARNING)):
                lines.extend([
                    f"\n[{issue.severity.value.upper()}] {issue.title} ({issue.issue_id})",
                    f"  Category: {issue.category.value.replace('_', ' ').title()}",
                    f"  Field: {issue.affected_field}",
                    f"  Description: {issue.description}",
                    f"  Recommendation: {issue.recommendation}",
                ])
        
        if score.recommendations:
            lines.extend([
                f"\nActionable Recommendations:",
                "-" * 80,
            ])
            for i, rec in enumerate(score.recommendations, 1):
                lines.append(f"{i}. {rec}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


def create_scorer() -> ComplianceScorer:
    """Factory function to create a ComplianceScorer instance"""
    return ComplianceScorer()
