"""
ChatGPT Product Feed Schema Validator - Comprehensive Demo

This script demonstrates all the enhanced features for Batch 1:
1. Complete ChatGPT product feed specification
2. Field-level and schema-level validation
3. Schema management (save/load/compare)
4. Batch validation with detailed reports

Author: deepakgargct
Date: 2026-01-06
"""

import json
import tempfile
import os
from chatgpt_feed_spec import (
    Product, ProductFeed, FeedFormat, CurrencyCode,
    ProductAvailability, ProductCondition, ChatGPTFieldSpecification
)
from schema_manager import SchemaManager, ProductFeedSchema
from chatgpt_schema_validator import ChatGPTSchemaValidator


def demo_field_specifications():
    """Demonstrate ChatGPT field specifications"""
    print("=" * 80)
    print("DEMO 1: ChatGPT Field Specifications")
    print("=" * 80)
    
    # Get all field specifications
    specs = ChatGPTFieldSpecification.get_field_specs()
    print(f"\nTotal fields defined: {len(specs)}")
    
    # Show required fields
    required = ChatGPTFieldSpecification.get_required_fields()
    print(f"\nRequired fields ({len(required)}):")
    for field in required:
        spec = specs[field]
        print(f"  - {field}: {spec.description}")
    
    # Show optional fields
    optional = ChatGPTFieldSpecification.get_optional_fields()
    print(f"\nOptional fields ({len(optional)}):")
    for field in optional[:5]:  # Show first 5
        spec = specs[field]
        print(f"  - {field}: {spec.description}")
    
    # Show field dependencies
    deps = ChatGPTFieldSpecification.get_field_dependencies()
    print(f"\nField dependencies:")
    for field, dep_list in deps.items():
        print(f"  - {field} requires: {', '.join(dep_list)}")
    
    # Export to JSON Schema
    json_schema = ChatGPTFieldSpecification.to_json_schema()
    print(f"\nJSON Schema exported with {len(json_schema['properties'])} properties")


def demo_product_validation():
    """Demonstrate product creation and validation"""
    print("\n" + "=" * 80)
    print("DEMO 2: Product Creation and Validation")
    print("=" * 80)
    
    # Create a valid product
    print("\n--- Creating Valid Product ---")
    valid_product = Product(
        enable_search=True,
        enable_checkout=True,
        id="DEMO-001",
        title="Wireless Bluetooth Headphones",
        description="Premium wireless headphones with active noise cancellation, 30-hour battery life, and superior sound quality.",
        price=149.99,
        currency="USD",
        availability="in_stock",
        image_link="https://example.com/headphones.jpg",
        link="https://example.com/products/headphones",
        category="Electronics",
        brand="AudioTech Pro",
        condition=ProductCondition.NEW,
        sku="AUDIO-WH-001",
        gtin="1234567890123",
        rating=4.5,
        reviews_count=350,
        sale_price=129.99
    )
    print("✓ Valid product created successfully")
    print(f"  Product ID: {valid_product.id}")
    print(f"  Title: {valid_product.title}")
    print(f"  Price: ${valid_product.price} (Sale: ${valid_product.sale_price})")
    
    # Try to create an invalid product (dependency violation)
    print("\n--- Testing Dependency Rules ---")
    try:
        invalid_product = Product(
            enable_search=False,
            enable_checkout=True,  # This should fail
            id="DEMO-002",
            title="USB Cable",
            description="High-quality USB-C cable for fast charging.",
            price=19.99,
            currency="USD",
            availability="in_stock",
            image_link="https://example.com/cable.jpg",
            link="https://example.com/products/cable"
        )
    except ValueError as e:
        print(f"✓ Dependency rule enforced: {e}")


def demo_schema_validator():
    """Demonstrate comprehensive schema validation"""
    print("\n" + "=" * 80)
    print("DEMO 3: ChatGPT Schema Validator")
    print("=" * 80)
    
    validator = ChatGPTSchemaValidator()
    
    # Validate a valid product
    print("\n--- Validating Valid Product ---")
    valid_data = {
        "enable_search": True,
        "enable_checkout": True,
        "id": "PROD-001",
        "title": "Smartphone Case",
        "description": "Durable protective case for smartphones with shock absorption and premium materials.",
        "price": 24.99,
        "currency": "USD",
        "availability": "in_stock",
        "image_link": "https://example.com/case.jpg",
        "link": "https://example.com/products/case",
        "category": "Accessories",
        "brand": "ProtectPlus",
        "rating": 4.8,
        "reviews_count": 520
    }
    
    result = validator.validate_product(valid_data)
    print(f"Validation Result: {'VALID' if result.is_valid else 'INVALID'}")
    print(f"Score: {result.score}/100")
    print(f"Errors: {len(result.get_all_errors())}")
    print(f"Warnings: {len(result.get_all_warnings())}")
    
    # Validate an invalid product
    print("\n--- Validating Invalid Product ---")
    invalid_data = {
        "enable_search": False,
        "enable_checkout": True,  # Dependency error
        "id": "",  # Empty ID
        "title": "USB",  # Too short title
        "description": "Short",  # Too short description
        "price": -5,  # Negative price
        "currency": "US",  # Invalid currency code
        "availability": "available",  # Invalid enum value
        "image_link": "not-a-url",  # Invalid URL
        "link": "example.com/product"  # Missing protocol
    }
    
    result = validator.validate_product(invalid_data)
    print(f"Validation Result: {'VALID' if result.is_valid else 'INVALID'}")
    print(f"Score: {result.score}/100")
    print(f"Errors: {len(result.get_all_errors())}")
    
    # Show detailed report
    print("\nDetailed Validation Report:")
    print(validator.generate_report(result))


def demo_batch_validation():
    """Demonstrate batch validation"""
    print("\n" + "=" * 80)
    print("DEMO 4: Batch Validation")
    print("=" * 80)
    
    validator = ChatGPTSchemaValidator()
    
    products = [
        {
            "enable_search": True,
            "enable_checkout": True,
            "id": "BATCH-001",
            "title": "Product 1",
            "description": "Valid product 1 with proper description and all required fields.",
            "price": 29.99,
            "currency": "USD",
            "availability": "in_stock",
            "image_link": "https://example.com/p1.jpg",
            "link": "https://example.com/p1"
        },
        {
            "enable_search": True,
            "enable_checkout": True,
            "id": "BATCH-002",
            "title": "Product 2",
            "description": "Valid product 2 with proper description and all required fields.",
            "price": 49.99,
            "currency": "USD",
            "availability": "in_stock",
            "image_link": "https://example.com/p2.jpg",
            "link": "https://example.com/p2"
        },
        {
            "id": "BATCH-003",
            "title": "Invalid Product"
            # Missing many required fields
        },
        {
            "enable_search": True,
            "enable_checkout": True,
            "id": "BATCH-004",
            "title": "Product 4",
            "description": "Another valid product with all required fields present.",
            "price": 79.99,
            "currency": "EUR",
            "availability": "preorder",
            "image_link": "https://example.com/p4.jpg",
            "link": "https://example.com/p4"
        }
    ]
    
    batch_result = validator.validate_batch(products)
    
    print(f"Total Products: {batch_result.total_products}")
    print(f"Valid Products: {batch_result.valid_products}")
    print(f"Invalid Products: {batch_result.invalid_products}")
    print(f"Success Rate: {batch_result.to_dict()['success_rate']}%")
    
    print("\nBatch Validation Report:")
    print(validator.generate_report(batch_result))


def demo_schema_management():
    """Demonstrate schema management features"""
    print("\n" + "=" * 80)
    print("DEMO 5: Schema Management")
    print("=" * 80)
    
    # Create a temporary directory for demo files
    temp_dir = tempfile.mkdtemp()
    
    # Create a schema
    print("\n--- Creating and Saving Schema ---")
    schema1 = ProductFeedSchema()
    print(f"Schema created: {schema1.schema_name}")
    print(f"Total attributes: {len(schema1.attributes)}")
    
    # Save to file
    schema_path = os.path.join(temp_dir, 'demo_schema1.json')
    schema1.save_to_file(schema_path)
    print(f"✓ Schema saved to {schema_path}")
    
    # Load from file
    loaded_schema = SchemaManager.load_from_file(schema_path)
    print(f"✓ Schema loaded: {loaded_schema.schema_name}")
    
    # Create a second schema for comparison
    print("\n--- Schema Comparison ---")
    schema2 = ProductFeedSchema()
    schema2.add_low_attribute(
        'custom_field',
        'Custom field for testing',
        data_type='string'
    )
    
    comparison = schema1.compare_with(schema2)
    print(f"Added attributes: {comparison['added_attributes']}")
    print(f"Removed attributes: {comparison['removed_attributes']}")
    print(f"Modified attributes: {len(comparison['modified_attributes'])}")
    print(f"Unchanged attributes: {len(comparison['unchanged_attributes'])}")
    
    # Generate diff
    print("\n--- Schema Diff ---")
    diff = schema1.diff(schema2)
    print(diff)
    
    # Validate against ChatGPT spec
    print("\n--- Validate Against ChatGPT Specification ---")
    is_valid, errors = schema1.validate_against_chatgpt_spec()
    print(f"Valid: {is_valid}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for error in errors[:3]:  # Show first 3
            print(f"  - {error}")
    
    # Merge schemas
    print("\n--- Schema Merging ---")
    merged = schema1.merge_with(schema2, conflict_resolution='this')
    print(f"Merged schema: {merged.schema_name}")
    print(f"Total attributes in merged: {len(merged.attributes)}")


def demo_json_export():
    """Demonstrate JSON export capabilities"""
    print("\n" + "=" * 80)
    print("DEMO 6: JSON Export and Integration")
    print("=" * 80)
    
    # Create a complete product feed
    product = Product(
        enable_search=True,
        enable_checkout=True,
        id="EXPORT-001",
        title="Export Demo Product",
        description="This product demonstrates JSON export capabilities with all fields.",
        price=99.99,
        currency="USD",
        availability="in_stock",
        image_link="https://example.com/export-demo.jpg",
        link="https://example.com/products/export-demo",
        category="Demo",
        brand="DemoBrand",
        condition=ProductCondition.NEW,
        rating=5.0,
        reviews_count=100
    )
    
    feed = ProductFeed(
        feed_id="DEMO-FEED-001",
        name="Demo Product Feed",
        format=FeedFormat.JSON,
        currency=CurrencyCode.USD,
        products=[product],
        language="en",
        country="US"
    )
    
    # Export to JSON
    feed_json = feed.to_json()
    print("Product Feed JSON Export:")
    print(feed_json[:500] + "...")  # Show first 500 chars
    
    # Validate the exported product
    validator = ChatGPTSchemaValidator()
    product_dict = product.to_dict()
    result = validator.validate_product(product_dict)
    
    print(f"\nValidation of exported product:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Score: {result.score}/100")


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "ChatGPT Product Feed Schema Validator - Comprehensive Demo".center(78) + "║")
    print("║" + "Batch 1 Implementation".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    demo_field_specifications()
    demo_product_validation()
    demo_schema_validator()
    demo_batch_validation()
    demo_schema_management()
    demo_json_export()
    
    print("\n" + "=" * 80)
    print("All demonstrations completed successfully!")
    print("=" * 80)
    print("\nKey Features Implemented:")
    print("  ✓ Complete ChatGPT product feed specification")
    print("  ✓ Field-level validation with constraints")
    print("  ✓ Schema-level validation with dependencies")
    print("  ✓ Batch validation support")
    print("  ✓ Schema management (save/load/compare/merge)")
    print("  ✓ Detailed validation reports")
    print("  ✓ JSON export capabilities")
    print("\n")


if __name__ == "__main__":
    main()
