"""
Test suite for ChatGPT Product Feed Schema Validator

Basic tests to validate the core functionality of the enhanced modules.
"""

import pytest
import json
import os
from chatgpt_feed_spec import (
    Product, ChatGPTFieldSpecification, ProductCondition,
    ProductAvailability, CurrencyCode, FieldSpec
)
from schema_manager import SchemaManager, ProductFeedSchema
from chatgpt_schema_validator import ChatGPTSchemaValidator


class TestChatGPTFieldSpecification:
    """Test ChatGPT field specifications"""
    
    def test_get_field_specs(self):
        """Test getting field specifications"""
        specs = ChatGPTFieldSpecification.get_field_specs()
        assert isinstance(specs, dict)
        assert len(specs) > 0
        assert 'enable_search' in specs
        assert 'enable_checkout' in specs
        assert 'id' in specs
        assert 'title' in specs
    
    def test_required_fields(self):
        """Test required fields list"""
        required = ChatGPTFieldSpecification.get_required_fields()
        assert isinstance(required, list)
        assert 'enable_search' in required
        assert 'enable_checkout' in required
        assert 'id' in required
        assert 'title' in required
        assert 'description' in required
        assert 'price' in required
        assert 'currency' in required
        assert 'availability' in required
        assert 'image_link' in required
        assert 'link' in required
    
    def test_optional_fields(self):
        """Test optional fields list"""
        optional = ChatGPTFieldSpecification.get_optional_fields()
        assert isinstance(optional, list)
        assert 'category' in optional
        assert 'brand' in optional
        assert 'condition' in optional
        assert 'sku' in optional
        assert 'gtin' in optional
    
    def test_field_dependencies(self):
        """Test field dependencies"""
        deps = ChatGPTFieldSpecification.get_field_dependencies()
        assert isinstance(deps, dict)
        assert 'enable_checkout' in deps
        assert 'enable_search' in deps['enable_checkout']
    
    def test_to_json_schema(self):
        """Test JSON schema export"""
        schema = ChatGPTFieldSpecification.to_json_schema()
        assert '$schema' in schema
        assert 'properties' in schema
        assert 'required' in schema
        assert 'enable_search' in schema['properties']


class TestProduct:
    """Test Product class with ChatGPT specification"""
    
    def test_valid_product_creation(self):
        """Test creating a valid product"""
        product = Product(
            enable_search=True,
            enable_checkout=True,
            id="PROD001",
            title="Test Product",
            description="This is a test product description with sufficient length.",
            price=99.99,
            currency="USD",
            availability="in_stock",
            image_link="https://example.com/image.jpg",
            link="https://example.com/product"
        )
        assert product.id == "PROD001"
        assert product.enable_search is True
        assert product.enable_checkout is True
    
    def test_dependency_rule_enforcement(self):
        """Test that enable_checkout requires enable_search"""
        with pytest.raises(ValueError, match="enable_checkout requires enable_search"):
            Product(
                enable_search=False,
                enable_checkout=True,
                id="PROD002",
                title="Test Product",
                description="This is a test product description.",
                price=99.99,
                currency="USD",
                availability="in_stock",
                image_link="https://example.com/image.jpg",
                link="https://example.com/product"
            )
    
    def test_empty_id_validation(self):
        """Test that empty ID is rejected"""
        with pytest.raises(ValueError, match="Product ID cannot be empty"):
            Product(
                enable_search=True,
                enable_checkout=False,
                id="",
                title="Test Product",
                description="This is a test product description.",
                price=99.99,
                currency="USD",
                availability="in_stock",
                image_link="https://example.com/image.jpg",
                link="https://example.com/product"
            )
    
    def test_invalid_url_validation(self):
        """Test URL validation"""
        with pytest.raises(ValueError, match="must be a valid HTTP"):
            Product(
                enable_search=True,
                enable_checkout=False,
                id="PROD003",
                title="Test Product",
                description="This is a test product description.",
                price=99.99,
                currency="USD",
                availability="in_stock",
                image_link="not-a-url",
                link="https://example.com/product"
            )
    
    def test_price_validation(self):
        """Test price validation"""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            Product(
                enable_search=True,
                enable_checkout=False,
                id="PROD004",
                title="Test Product",
                description="This is a test product description.",
                price=-10.0,
                currency="USD",
                availability="in_stock",
                image_link="https://example.com/image.jpg",
                link="https://example.com/product"
            )
    
    def test_sale_price_validation(self):
        """Test sale price validation"""
        with pytest.raises(ValueError, match="Sale price cannot be greater"):
            Product(
                enable_search=True,
                enable_checkout=False,
                id="PROD005",
                title="Test Product",
                description="This is a test product description.",
                price=50.0,
                currency="USD",
                availability="in_stock",
                image_link="https://example.com/image.jpg",
                link="https://example.com/product",
                sale_price=100.0
            )
    
    def test_product_to_dict(self):
        """Test product to dictionary conversion"""
        product = Product(
            enable_search=True,
            enable_checkout=True,
            id="PROD006",
            title="Test Product",
            description="This is a test product description.",
            price=99.99,
            currency="USD",
            availability="in_stock",
            image_link="https://example.com/image.jpg",
            link="https://example.com/product",
            category="Electronics",
            brand="TestBrand"
        )
        product_dict = product.to_dict()
        assert product_dict['id'] == "PROD006"
        assert product_dict['enable_search'] is True
        assert product_dict['category'] == "Electronics"
        assert product_dict['brand'] == "TestBrand"


class TestSchemaManager:
    """Test SchemaManager enhancements"""
    
    def test_save_and_load_schema(self, tmp_path):
        """Test saving and loading schema to/from JSON"""
        schema = ProductFeedSchema()
        filepath = tmp_path / "test_schema.json"
        
        schema.save_to_file(str(filepath))
        assert filepath.exists()
        
        loaded_schema = SchemaManager.load_from_file(str(filepath))
        assert loaded_schema.schema_name == schema.schema_name
        assert len(loaded_schema.attributes) == len(schema.attributes)
    
    def test_schema_comparison(self):
        """Test schema comparison"""
        schema1 = ProductFeedSchema()
        schema2 = ProductFeedSchema()
        schema2.add_low_attribute('test_field', 'Test field')
        
        comparison = schema1.compare_with(schema2)
        assert 'added_attributes' in comparison
        assert 'removed_attributes' in comparison
        assert 'test_field' in comparison['removed_attributes']
    
    def test_schema_diff(self):
        """Test schema diff generation"""
        schema1 = ProductFeedSchema()
        schema2 = ProductFeedSchema()
        schema2.add_low_attribute('new_field', 'New field')
        
        diff = schema1.diff(schema2)
        assert 'Schema Comparison' in diff
        assert 'Removed Attributes' in diff
    
    def test_schema_merge(self):
        """Test schema merging"""
        schema1 = ProductFeedSchema()
        schema2 = SchemaManager(schema_name="TestSchema")
        schema2.add_low_attribute('extra_field', 'Extra field')
        
        merged = schema1.merge_with(schema2, conflict_resolution='this')
        assert 'extra_field' in merged.attributes
        assert len(merged.attributes) > len(schema1.attributes)


class TestChatGPTSchemaValidator:
    """Test ChatGPTSchemaValidator"""
    
    def test_valid_product_validation(self):
        """Test validating a valid product"""
        validator = ChatGPTSchemaValidator()
        product_data = {
            "enable_search": True,
            "enable_checkout": True,
            "id": "PROD001",
            "title": "Test Product",
            "description": "This is a test product with sufficient description length.",
            "price": 99.99,
            "currency": "USD",
            "availability": "in_stock",
            "image_link": "https://example.com/image.jpg",
            "link": "https://example.com/product"
        }
        
        result = validator.validate_product(product_data)
        assert result.is_valid is True
        assert result.score == 100.0
        assert len(result.get_all_errors()) == 0
    
    def test_invalid_product_validation(self):
        """Test validating an invalid product"""
        validator = ChatGPTSchemaValidator()
        product_data = {
            "enable_search": False,
            "enable_checkout": True,  # Error: dependency
            "id": "",  # Error: empty
            "title": "Test",
            "description": "Short",  # Error: too short
            "price": -10,  # Error: negative
            "currency": "US",  # Error: invalid format
            "availability": "available",  # Error: invalid enum
            "image_link": "not-a-url",  # Error: invalid URL
            "link": "example.com"  # Error: missing protocol
        }
        
        result = validator.validate_product(product_data)
        assert result.is_valid is False
        assert len(result.get_all_errors()) > 0
        assert result.score < 100.0
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields"""
        validator = ChatGPTSchemaValidator()
        product_data = {
            "id": "PROD001",
            "title": "Test Product"
            # Missing many required fields
        }
        
        result = validator.validate_product(product_data)
        assert result.is_valid is False
        errors = result.get_all_errors()
        assert len(errors) > 0
        # Check for specific missing fields
        error_messages = [e.message for e in errors]
        assert any("enable_search" in msg for msg in error_messages)
    
    def test_batch_validation(self):
        """Test batch validation"""
        validator = ChatGPTSchemaValidator()
        products = [
            {
                "enable_search": True,
                "enable_checkout": True,
                "id": "PROD001",
                "title": "Valid Product",
                "description": "This is a valid product with proper description.",
                "price": 99.99,
                "currency": "USD",
                "availability": "in_stock",
                "image_link": "https://example.com/image1.jpg",
                "link": "https://example.com/product1"
            },
            {
                "id": "PROD002",
                "title": "Invalid Product"
                # Missing required fields
            }
        ]
        
        batch_result = validator.validate_batch(products)
        assert batch_result.total_products == 2
        assert batch_result.valid_products == 1
        assert batch_result.invalid_products == 1
    
    def test_validation_report_generation(self):
        """Test validation report generation"""
        validator = ChatGPTSchemaValidator()
        product_data = {
            "enable_search": True,
            "enable_checkout": True,
            "id": "PROD001",
            "title": "Test Product",
            "description": "This is a test product description.",
            "price": 99.99,
            "currency": "USD",
            "availability": "in_stock",
            "image_link": "https://example.com/image.jpg",
            "link": "https://example.com/product"
        }
        
        result = validator.validate_product(product_data)
        report = validator.generate_report(result)
        
        assert isinstance(report, str)
        assert "Product Validation Report" in report
        assert "PROD001" in report
        assert "Status:" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
