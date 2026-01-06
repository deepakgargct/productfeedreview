"""
ChatGPT Product Feed Schema Specification
==========================================

This module contains the complete ChatGPT Product Feed specification
as a structured Python dictionary with comprehensive validation rules.

The specification defines required fields, data types, constraints, and
validation logic for product feed data intended for use with ChatGPT
and other AI/ML applications.

Created: 2026-01-06 12:18:11 UTC
"""

CHATGPT_PRODUCT_FEED_SPEC = {
    "feed_metadata": {
        "description": "Feed-level metadata and configuration",
        "required": True,
        "fields": {
            "feed_name": {
                "type": "string",
                "description": "Name of the product feed",
                "required": True,
                "max_length": 255,
                "pattern": "^[a-zA-Z0-9_\\-\\s]+$",
                "validation_rules": {
                    "non_empty": True,
                    "allow_special_chars": ["_", "-"],
                }
            },
            "feed_version": {
                "type": "string",
                "description": "Version identifier for the feed",
                "required": True,
                "pattern": "^\\d+\\.\\d+\\.\\d+$",
                "validation_rules": {
                    "semantic_versioning": True,
                }
            },
            "feed_language": {
                "type": "string",
                "description": "Primary language code (ISO 639-1)",
                "required": True,
                "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
                "allowed_values": [
                    "en", "es", "fr", "de", "it", "pt", "nl", "ru", "zh", "ja", "ko"
                ],
                "validation_rules": {
                    "iso_639_1_compliant": True,
                }
            },
            "feed_currency": {
                "type": "string",
                "description": "Primary currency code (ISO 4217)",
                "required": True,
                "pattern": "^[A-Z]{3}$",
                "validation_rules": {
                    "iso_4217_compliant": True,
                }
            },
            "last_modified": {
                "type": "datetime",
                "description": "Last modification timestamp (ISO 8601 format)",
                "required": True,
                "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z?$",
                "validation_rules": {
                    "iso_8601_compliant": True,
                    "not_future_dated": True,
                }
            },
            "total_products": {
                "type": "integer",
                "description": "Total number of products in the feed",
                "required": True,
                "minimum": 1,
                "validation_rules": {
                    "positive_integer": True,
                }
            },
            "feed_url": {
                "type": "string",
                "description": "URL where the feed is hosted",
                "required": False,
                "pattern": "^https?://[^\\s]+$",
                "validation_rules": {
                    "valid_url": True,
                    "https_preferred": True,
                }
            },
        }
    },
    "products": {
        "description": "Array of product objects",
        "required": True,
        "type": "array",
        "item_schema": {
            "type": "object",
            "required_fields": [
                "id",
                "title",
                "price",
                "currency",
                "product_type",
                "availability",
            ],
            "fields": {
                "id": {
                    "type": "string",
                    "description": "Unique product identifier (SKU or internal ID)",
                    "required": True,
                    "max_length": 100,
                    "pattern": "^[a-zA-Z0-9_\\-]+$",
                    "validation_rules": {
                        "unique_across_feed": True,
                        "non_empty": True,
                        "allow_special_chars": ["_", "-"],
                    }
                },
                "title": {
                    "type": "string",
                    "description": "Product title or name",
                    "required": True,
                    "min_length": 3,
                    "max_length": 150,
                    "validation_rules": {
                        "non_empty": True,
                        "no_excessive_caps": True,
                        "no_keyword_stuffing": True,
                    }
                },
                "description": {
                    "type": "string",
                    "description": "Detailed product description",
                    "required": False,
                    "min_length": 10,
                    "max_length": 2000,
                    "validation_rules": {
                        "html_allowed": False,
                        "plain_text_only": True,
                    }
                },
                "price": {
                    "type": "decimal",
                    "description": "Product price",
                    "required": True,
                    "minimum": 0,
                    "decimal_places": 2,
                    "validation_rules": {
                        "positive_or_zero": True,
                        "two_decimal_places": True,
                        "numeric_only": True,
                    }
                },
                "original_price": {
                    "type": "decimal",
                    "description": "Original/MSRP price before discount",
                    "required": False,
                    "minimum": 0,
                    "decimal_places": 2,
                    "validation_rules": {
                        "greater_than_or_equal_sale_price": True,
                        "optional_field": True,
                    }
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code (ISO 4217)",
                    "required": True,
                    "pattern": "^[A-Z]{3}$",
                    "validation_rules": {
                        "iso_4217_compliant": True,
                    }
                },
                "product_type": {
                    "type": "string",
                    "description": "Product category/type",
                    "required": True,
                    "max_length": 100,
                    "allowed_values": [
                        "electronics", "clothing", "home", "beauty", "food",
                        "sports", "books", "toys", "furniture", "automotive",
                        "jewelry", "office", "garden", "health", "pet", "other"
                    ],
                    "validation_rules": {
                        "predefined_list": True,
                    }
                },
                "brand": {
                    "type": "string",
                    "description": "Product brand or manufacturer",
                    "required": False,
                    "max_length": 100,
                    "validation_rules": {
                        "no_excessive_caps": True,
                    }
                },
                "manufacturer": {
                    "type": "string",
                    "description": "Manufacturer name",
                    "required": False,
                    "max_length": 150,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "sku": {
                    "type": "string",
                    "description": "Stock Keeping Unit",
                    "required": False,
                    "max_length": 50,
                    "validation_rules": {
                        "alphanumeric": True,
                    }
                },
                "gtin": {
                    "type": "string",
                    "description": "Global Trade Item Number (EAN, UPC)",
                    "required": False,
                    "pattern": "^\\d{8,14}$",
                    "validation_rules": {
                        "numeric_only": True,
                        "length_8_to_14": True,
                    }
                },
                "availability": {
                    "type": "string",
                    "description": "Product availability status",
                    "required": True,
                    "allowed_values": [
                        "in_stock",
                        "out_of_stock",
                        "pre_order",
                        "discontinued",
                        "coming_soon",
                        "backorder"
                    ],
                    "validation_rules": {
                        "predefined_list": True,
                    }
                },
                "stock_quantity": {
                    "type": "integer",
                    "description": "Number of units in stock",
                    "required": False,
                    "minimum": 0,
                    "validation_rules": {
                        "non_negative_integer": True,
                        "optional_field": True,
                    }
                },
                "url": {
                    "type": "string",
                    "description": "Product page URL",
                    "required": True,
                    "pattern": "^https?://[^\\s]+$",
                    "max_length": 500,
                    "validation_rules": {
                        "valid_url": True,
                        "https_preferred": True,
                        "unique_across_feed": False,
                    }
                },
                "image_url": {
                    "type": "string",
                    "description": "Primary product image URL",
                    "required": True,
                    "pattern": "^https?://[^\\s]+\\.(jpg|jpeg|png|webp|gif)$",
                    "max_length": 500,
                    "validation_rules": {
                        "valid_url": True,
                        "https_preferred": True,
                        "valid_image_extension": ["jpg", "jpeg", "png", "webp", "gif"],
                    }
                },
                "image_urls": {
                    "type": "array",
                    "description": "Additional product images",
                    "required": False,
                    "max_items": 10,
                    "item_type": "string",
                    "validation_rules": {
                        "valid_urls": True,
                        "https_preferred": True,
                        "max_10_images": True,
                    }
                },
                "rating": {
                    "type": "decimal",
                    "description": "Product rating (0-5 scale)",
                    "required": False,
                    "minimum": 0,
                    "maximum": 5,
                    "decimal_places": 2,
                    "validation_rules": {
                        "within_0_to_5_range": True,
                        "two_decimal_places": True,
                    }
                },
                "review_count": {
                    "type": "integer",
                    "description": "Number of customer reviews",
                    "required": False,
                    "minimum": 0,
                    "validation_rules": {
                        "non_negative_integer": True,
                    }
                },
                "shipping_cost": {
                    "type": "decimal",
                    "description": "Shipping cost for the product",
                    "required": False,
                    "minimum": 0,
                    "decimal_places": 2,
                    "validation_rules": {
                        "positive_or_zero": True,
                        "two_decimal_places": True,
                    }
                },
                "shipping_time": {
                    "type": "string",
                    "description": "Estimated shipping time (e.g., '2-5 business days')",
                    "required": False,
                    "max_length": 100,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "return_policy": {
                    "type": "string",
                    "description": "Product return policy",
                    "required": False,
                    "max_length": 500,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "warranty": {
                    "type": "string",
                    "description": "Warranty information",
                    "required": False,
                    "max_length": 300,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "color": {
                    "type": "string",
                    "description": "Product color",
                    "required": False,
                    "max_length": 50,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "size": {
                    "type": "string",
                    "description": "Product size/dimensions",
                    "required": False,
                    "max_length": 100,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "weight": {
                    "type": "decimal",
                    "description": "Product weight",
                    "required": False,
                    "minimum": 0,
                    "decimal_places": 2,
                    "validation_rules": {
                        "positive_or_zero": True,
                        "optional_field": True,
                    }
                },
                "dimensions": {
                    "type": "object",
                    "description": "Product dimensions",
                    "required": False,
                    "fields": {
                        "length": {
                            "type": "decimal",
                            "minimum": 0,
                            "decimal_places": 2,
                        },
                        "width": {
                            "type": "decimal",
                            "minimum": 0,
                            "decimal_places": 2,
                        },
                        "height": {
                            "type": "decimal",
                            "minimum": 0,
                            "decimal_places": 2,
                        },
                        "unit": {
                            "type": "string",
                            "allowed_values": ["cm", "inches", "m"],
                        }
                    },
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "material": {
                    "type": "string",
                    "description": "Product material composition",
                    "required": False,
                    "max_length": 200,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "condition": {
                    "type": "string",
                    "description": "Product condition",
                    "required": False,
                    "allowed_values": [
                        "new",
                        "refurbished",
                        "used",
                        "like_new",
                        "fair",
                        "good"
                    ],
                    "validation_rules": {
                        "predefined_list": True,
                    }
                },
                "tags": {
                    "type": "array",
                    "description": "Product tags or keywords",
                    "required": False,
                    "max_items": 20,
                    "item_type": "string",
                    "max_item_length": 50,
                    "validation_rules": {
                        "max_20_tags": True,
                        "no_duplicate_tags": True,
                    }
                },
                "categories": {
                    "type": "array",
                    "description": "Product category hierarchy",
                    "required": False,
                    "max_items": 5,
                    "item_type": "string",
                    "validation_rules": {
                        "max_5_categories": True,
                        "no_duplicate_categories": True,
                    }
                },
                "related_products": {
                    "type": "array",
                    "description": "Related product IDs",
                    "required": False,
                    "max_items": 10,
                    "item_type": "string",
                    "validation_rules": {
                        "max_10_related_products": True,
                        "no_self_reference": True,
                    }
                },
                "expiration_date": {
                    "type": "datetime",
                    "description": "Product/offer expiration date (ISO 8601)",
                    "required": False,
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z?$",
                    "validation_rules": {
                        "iso_8601_compliant": True,
                        "not_past_dated": False,
                    }
                },
                "created_date": {
                    "type": "datetime",
                    "description": "Product creation date (ISO 8601)",
                    "required": False,
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z?$",
                    "validation_rules": {
                        "iso_8601_compliant": True,
                        "not_future_dated": True,
                    }
                },
                "updated_date": {
                    "type": "datetime",
                    "description": "Last product update date (ISO 8601)",
                    "required": False,
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z?$",
                    "validation_rules": {
                        "iso_8601_compliant": True,
                        "not_future_dated": True,
                    }
                },
                "seo_title": {
                    "type": "string",
                    "description": "SEO optimized page title",
                    "required": False,
                    "min_length": 10,
                    "max_length": 60,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "seo_description": {
                    "type": "string",
                    "description": "SEO meta description",
                    "required": False,
                    "min_length": 20,
                    "max_length": 160,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "meta_keywords": {
                    "type": "array",
                    "description": "SEO keywords",
                    "required": False,
                    "max_items": 10,
                    "item_type": "string",
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "discount_percentage": {
                    "type": "decimal",
                    "description": "Discount percentage (0-100)",
                    "required": False,
                    "minimum": 0,
                    "maximum": 100,
                    "decimal_places": 2,
                    "validation_rules": {
                        "within_0_to_100_range": True,
                    }
                },
                "supplier": {
                    "type": "string",
                    "description": "Product supplier/vendor name",
                    "required": False,
                    "max_length": 150,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "supplier_id": {
                    "type": "string",
                    "description": "Supplier/vendor unique identifier",
                    "required": False,
                    "max_length": 100,
                    "validation_rules": {
                        "optional_field": True,
                    }
                },
                "is_active": {
                    "type": "boolean",
                    "description": "Whether product is currently active",
                    "required": False,
                    "default": True,
                    "validation_rules": {
                        "boolean_field": True,
                    }
                },
                "is_featured": {
                    "type": "boolean",
                    "description": "Whether product is featured",
                    "required": False,
                    "default": False,
                    "validation_rules": {
                        "boolean_field": True,
                    }
                },
            }
        }
    },
    "validation_rules": {
        "description": "Global validation rules for the entire feed",
        "rules": {
            "unique_product_ids": {
                "description": "All product IDs must be unique within the feed",
                "severity": "error",
                "apply_to": "products[].id"
            },
            "price_currency_consistency": {
                "description": "Product currency should match feed currency or be explicitly specified",
                "severity": "warning",
                "apply_to": "products[].currency"
            },
            "valid_url_format": {
                "description": "All URLs must be valid and properly formatted",
                "severity": "error",
                "apply_to": ["products[].url", "products[].image_url", "feed_metadata.feed_url"]
            },
            "image_accessibility": {
                "description": "All product images must be accessible (HTTP 200 response)",
                "severity": "warning",
                "apply_to": "products[].image_url"
            },
            "product_title_quality": {
                "description": "Product titles should be descriptive and not contain excessive capitalization",
                "severity": "warning",
                "apply_to": "products[].title",
                "validation_criteria": {
                    "min_meaningful_words": 2,
                    "max_caps_ratio": 0.3,
                }
            },
            "price_consistency": {
                "description": "Sale price should not exceed original price",
                "severity": "error",
                "apply_to": ["products[].price", "products[].original_price"],
                "condition": "price <= original_price"
            },
            "stock_availability_logic": {
                "description": "Stock quantity should align with availability status",
                "severity": "warning",
                "apply_to": ["products[].availability", "products[].stock_quantity"],
                "rules": {
                    "in_stock": "stock_quantity > 0",
                    "out_of_stock": "stock_quantity == 0 or null",
                    "discontinued": "stock_quantity == 0"
                }
            },
            "date_consistency": {
                "description": "Updated date should be after or equal to created date",
                "severity": "warning",
                "apply_to": ["products[].created_date", "products[].updated_date"],
                "condition": "updated_date >= created_date"
            },
            "feed_size_limits": {
                "description": "Feed should not exceed practical size limits",
                "severity": "warning",
                "max_products": 50000,
                "max_feed_size_mb": 500,
            },
            "no_duplicate_urls": {
                "description": "Avoid duplicate product URLs (warnings only for same product)",
                "severity": "info",
                "apply_to": "products[].url"
            },
            "rating_review_consistency": {
                "description": "Products with ratings should have review counts",
                "severity": "info",
                "apply_to": ["products[].rating", "products[].review_count"],
                "condition": "if rating then review_count should exist"
            },
        }
    },
    "data_quality_metrics": {
        "description": "Metrics for assessing feed data quality",
        "metrics": {
            "completeness": {
                "description": "Percentage of required fields populated",
                "threshold": 95,
                "calculation": "(total_required_fields_populated / total_required_fields) * 100"
            },
            "accuracy": {
                "description": "Percentage of data points passing validation",
                "threshold": 99,
                "calculation": "(valid_data_points / total_data_points) * 100"
            },
            "consistency": {
                "description": "Percentage of data following consistency rules",
                "threshold": 98,
                "calculation": "(consistent_data_points / total_data_points) * 100"
            },
            "timeliness": {
                "description": "Feed recency - last update within acceptable window",
                "threshold": "24 hours",
                "calculation": "current_time - feed_last_modified"
            }
        }
    },
    "error_codes": {
        "INVALID_TYPE": {
            "code": "E001",
            "message": "Field has invalid data type",
            "severity": "error"
        },
        "MISSING_REQUIRED": {
            "code": "E002",
            "message": "Required field is missing",
            "severity": "error"
        },
        "VALUE_OUT_OF_RANGE": {
            "code": "E003",
            "message": "Field value is outside acceptable range",
            "severity": "error"
        },
        "INVALID_FORMAT": {
            "code": "E004",
            "message": "Field format does not match expected pattern",
            "severity": "error"
        },
        "INVALID_URL": {
            "code": "E005",
            "message": "URL is invalid or malformed",
            "severity": "error"
        },
        "DUPLICATE_ID": {
            "code": "E006",
            "message": "Product ID is duplicated in feed",
            "severity": "error"
        },
        "PRICE_INCONSISTENCY": {
            "code": "W001",
            "message": "Sale price exceeds original price",
            "severity": "warning"
        },
        "MISSING_IMAGE": {
            "code": "W002",
            "message": "Product image is inaccessible",
            "severity": "warning"
        },
        "INVALID_ENCODING": {
            "code": "E007",
            "message": "Feed encoding is invalid (must be UTF-8)",
            "severity": "error"
        },
        "FIELD_TOO_LONG": {
            "code": "E008",
            "message": "Field value exceeds maximum length",
            "severity": "error"
        },
        "FIELD_TOO_SHORT": {
            "code": "E009",
            "message": "Field value is below minimum length",
            "severity": "error"
        },
        "INVALID_CURRENCY": {
            "code": "E010",
            "message": "Currency code is not valid ISO 4217",
            "severity": "error"
        },
    }
}


# Export for use in validators
__all__ = ["CHATGPT_PRODUCT_FEED_SPEC"]
