"""
Comprehensive URL Validator for Product Feed Review
Includes URL extraction, schema validation, and 70+ ChatGPT attributes
Created: 2026-01-06 13:45:05 UTC
Author: deepakgargct
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Set, Any
from urllib.parse import urlparse, parse_qs, urlunparse
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
from datetime import datetime


class URLScheme(Enum):
    """Supported URL schemes"""
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"
    FTPS = "ftps"


class ContentType(Enum):
    """Supported content types"""
    HTML = "text/html"
    JSON = "application/json"
    XML = "application/xml"
    PLAIN_TEXT = "text/plain"
    PDF = "application/pdf"
    IMAGE = "image/*"


@dataclass
class URLValidationResult:
    """Complete URL validation result with all attributes"""
    # Basic Properties (1-10)
    is_valid: bool
    url: str
    normalized_url: str
    scheme: str
    domain: str
    subdomain: str
    
    # Structure Properties (11-20)
    path: str
    query_string: str
    fragment: str
    port: Optional[int]
    username: Optional[str]
    password: Optional[str]
    
    # Security Properties (21-30)
    is_https: bool
    has_ssl_tls: bool
    certificate_valid: bool
    is_secure: bool
    suspicious_characters: List[str] = field(default_factory=list)
    contains_credentials: bool = False
    phishing_risk_score: float = 0.0
    malware_risk_score: float = 0.0
    spam_risk_score: float = 0.0
    
    # Content Properties (31-40)
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    content_encoding: Optional[str] = None
    charset: str = "utf-8"
    language: str = "en"
    is_responsive: bool = False
    cache_control: Optional[str] = None
    expires: Optional[str] = None
    etag: Optional[str] = None
    
    # SEO Properties (41-50)
    has_canonical_tag: bool = False
    has_robots_meta: bool = False
    has_og_tags: bool = False
    has_structured_data: bool = False
    domain_age_days: Optional[int] = None
    page_rank_score: float = 0.0
    alexa_rank: Optional[int] = None
    moz_domain_authority: float = 0.0
    moz_page_authority: float = 0.0
    backlink_count: int = 0
    
    # Performance Properties (51-60)
    response_time_ms: Optional[float] = None
    page_load_time_ms: Optional[float] = None
    ttfb_ms: Optional[float] = None
    is_cdn_enabled: bool = False
    compression_enabled: bool = False
    minification_enabled: bool = False
    lazy_loading_enabled: bool = False
    image_optimization_score: float = 0.0
    js_execution_score: float = 0.0
    css_rendering_score: float = 0.0
    
    # Compliance Properties (61-70)
    gdpr_compliant: bool = False
    ccpa_compliant: bool = False
    cookie_policy_present: bool = False
    privacy_policy_present: bool = False
    terms_of_service_present: bool = False
    accessibility_compliant: bool = False
    mobile_friendly: bool = False
    av_clean: bool = False
    safe_browsing: bool = False
    reputation_score: float = 0.0
    
    # Additional Properties (71+)
    parsed_query_params: Dict[str, List[str]] = field(default_factory=dict)
    path_segments: List[str] = field(default_factory=list)
    url_hash: str = ""
    extraction_timestamp: str = ""
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class URLValidator:
    """Comprehensive URL validation and extraction engine"""
    
    # URL Pattern Definitions
    URL_REGEX = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    EMAIL_URL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    IP_URL_REGEX = r'https?://(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
    
    # Suspicious patterns
    SUSPICIOUS_DOMAINS = {
        'bit.ly', 'tinyurl', 'short.link', 'ow.ly', 'goo.gl',
        'adf.ly', 'url.cn', 'j.mp', '0-day'
    }
    
    SUSPICIOUS_KEYWORDS = {
        'login', 'verify', 'confirm', 'update', 'secure', 'validate',
        'click', 'urgent', 'alert', 'warning', 'account', 'bank',
        'paypal', 'amazon', 'apple', 'microsoft', 'password', 'admin'
    }
    
    # Common TLDs
    VALID_TLDS = {
        'com', 'org', 'net', 'edu', 'gov', 'mil', 'co', 'uk', 'de',
        'fr', 'it', 'es', 'ru', 'jp', 'cn', 'in', 'br', 'mx', 'au',
        'ca', 'us', 'io', 'app', 'dev', 'tech', 'ai', 'ml', 'info',
        'biz', 'name', 'pro', 'mobi', 'asia', 'tel', 'travel', 'jobs',
        'post', 'ws', 'cc', 'tv', 'museum', 'aero', 'coop', 'xxx'
    }
    
    def __init__(self):
        """Initialize URL validator"""
        self.extracted_urls: Set[str] = set()
        self.validation_results: Dict[str, URLValidationResult] = {}
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract all URLs from text content
        
        Args:
            text: Input text to extract URLs from
            
        Returns:
            List of extracted URLs
        """
        urls = []
        
        # Extract HTTP/HTTPS URLs
        http_urls = re.findall(self.URL_REGEX, text)
        urls.extend(http_urls)
        
        # Extract IP-based URLs
        ip_urls = re.findall(self.IP_URL_REGEX, text)
        urls.extend(ip_urls)
        
        # Extract URLs without scheme
        no_scheme_urls = re.findall(r'(?:www\.)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?', text)
        for url in no_scheme_urls:
            if url not in urls and not re.match(r'^[a-zA-Z0-9]', url):
                if not url.startswith('http'):
                    url = 'https://' + url
                urls.append(url)
        
        # Normalize and deduplicate
        self.extracted_urls = set(urls)
        return list(self.extracted_urls)
    
    def validate_url(self, url: str) -> URLValidationResult:
        """
        Comprehensive URL validation with all 70+ attributes
        
        Args:
            url: URL to validate
            
        Returns:
            URLValidationResult with all validation details
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        result = URLValidationResult(
            is_valid=False,
            url=url,
            normalized_url="",
            scheme="",
            domain="",
            subdomain="",
            path="",
            query_string="",
            fragment="",
            port=None,
            username=None,
            password=None,
            is_https=False,
            has_ssl_tls=False,
            certificate_valid=False,
            is_secure=False,
            extraction_timestamp=timestamp
        )
        
        try:
            # Normalize URL
            normalized_url = self._normalize_url(url)
            result.normalized_url = normalized_url
            
            # Parse URL
            parsed = urlparse(normalized_url)
            
            # Basic Properties
            result.scheme = parsed.scheme or "https"
            result.port = parsed.port
            result.username = parsed.username
            result.password = parsed.password
            
            # Extract domain and subdomain
            result.domain = parsed.netloc
            domain_parts = parsed.netloc.split('.')
            if len(domain_parts) > 2:
                result.subdomain = '.'.join(domain_parts[:-2])
            
            # Path and query analysis
            result.path = parsed.path
            result.fragment = parsed.fragment
            result.query_string = parsed.query
            result.parsed_query_params = parse_qs(parsed.query)
            result.path_segments = [p for p in parsed.path.split('/') if p]
            
            # Security validation
            result.is_https = parsed.scheme == 'https'
            result.has_ssl_tls = result.is_https
            result.contains_credentials = bool(parsed.username or parsed.password)
            
            # Validate basic structure
            is_valid_structure = self._validate_url_structure(parsed)
            result.is_valid = is_valid_structure
            
            # Security checks
            result.phishing_risk_score = self._calculate_phishing_risk(normalized_url, parsed)
            result.malware_risk_score = self._calculate_malware_risk(normalized_url)
            result.spam_risk_score = self._calculate_spam_risk(normalized_url)
            
            # Security assessment
            result.certificate_valid = self._check_certificate_validity(result.domain)
            result.is_secure = (result.is_https and 
                              result.phishing_risk_score < 0.5 and
                              result.malware_risk_score < 0.5)
            
            # Suspicious character detection
            result.suspicious_characters = self._detect_suspicious_characters(normalized_url)
            
            # SEO Properties
            result.has_canonical_tag = self._check_canonical_tag(normalized_url)
            result.has_robots_meta = self._check_robots_meta(normalized_url)
            result.has_og_tags = self._check_og_tags(normalized_url)
            result.has_structured_data = self._check_structured_data(normalized_url)
            
            # Content Properties
            result.content_type = self._detect_content_type(normalized_url)
            result.is_responsive = self._check_responsive_design(normalized_url)
            
            # Performance assessment
            result.response_time_ms = self._estimate_response_time(result.domain)
            result.is_cdn_enabled = self._check_cdn_usage(result.domain)
            
            # Compliance checks
            result.gdpr_compliant = self._check_gdpr_compliance(normalized_url)
            result.ccpa_compliant = self._check_ccpa_compliance(normalized_url)
            result.cookie_policy_present = self._check_cookie_policy(normalized_url)
            result.privacy_policy_present = self._check_privacy_policy(normalized_url)
            result.mobile_friendly = self._check_mobile_friendly(normalized_url)
            result.safe_browsing = self._check_safe_browsing(result.domain)
            
            # Generate URL hash
            result.url_hash = hashlib.sha256(normalized_url.encode()).hexdigest()
            
            # Add validation to results cache
            self.validation_results[url] = result
            
        except Exception as e:
            result.validation_errors.append(f"Validation error: {str(e)}")
            result.is_valid = False
        
        return result
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to standard format"""
        url = url.strip()
        
        # Add scheme if missing
        if not re.match(r'^[a-z][a-z0-9+.-]*://', url):
            url = 'https://' + url
        
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Lowercase scheme and domain
        parsed = urlparse(url)
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        return normalized
    
    def _validate_url_structure(self, parsed) -> bool:
        """Validate URL structure"""
        # Check scheme
        if parsed.scheme not in [s.value for s in URLScheme]:
            return False
        
        # Check domain
        if not parsed.netloc:
            return False
        
        # Validate TLD
        domain_parts = parsed.netloc.split('.')
        if len(domain_parts) < 2:
            return False
        
        tld = domain_parts[-1].lower()
        # Allow numeric TLDs for IP addresses
        if not tld.isdigit() and tld not in self.VALID_TLDS:
            # Not necessarily invalid, just uncommon
            pass
        
        return True
    
    def _calculate_phishing_risk(self, url: str, parsed) -> float:
        """Calculate phishing risk score (0.0 to 1.0)"""
        risk_score = 0.0
        
        # Check for suspicious domains
        domain = parsed.netloc.lower()
        for suspicious in self.SUSPICIOUS_DOMAINS:
            if suspicious in domain:
                risk_score += 0.2
        
        # Check for suspicious keywords in URL
        url_lower = url.lower()
        suspicious_count = sum(1 for keyword in self.SUSPICIOUS_KEYWORDS if keyword in url_lower)
        risk_score += min(suspicious_count * 0.1, 0.3)
        
        # Check for IP address (higher risk)
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
            risk_score += 0.3
        
        # Check for encoded characters
        if '%' in url:
            risk_score += 0.15
        
        # Check for unusual port
        if parsed.port and parsed.port not in [80, 443, 8080, 8443]:
            risk_score += 0.1
        
        # Check for credentials in URL
        if parsed.username or parsed.password:
            risk_score += 0.25
        
        return min(risk_score, 1.0)
    
    def _calculate_malware_risk(self, url: str) -> float:
        """Calculate malware risk score"""
        risk_score = 0.0
        
        # Check for executable files
        executable_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js']
        if any(url.lower().endswith(ext) for ext in executable_extensions):
            risk_score += 0.5
        
        # Check for suspicious patterns
        if re.search(r'[^a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=]', url):
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _calculate_spam_risk(self, url: str) -> float:
        """Calculate spam risk score"""
        risk_score = 0.0
        
        # Check URL length
        if len(url) > 2048:
            risk_score += 0.2
        
        # Check for excessive parameters
        param_count = url.count('=')
        if param_count > 5:
            risk_score += 0.15
        
        # Check for tracking parameters
        tracking_params = ['utm_', 'fbclid', 'gclid', 'msclkid']
        for param in tracking_params:
            if param in url:
                risk_score += 0.05
        
        return min(risk_score, 1.0)
    
    def _detect_suspicious_characters(self, url: str) -> List[str]:
        """Detect suspicious characters in URL"""
        suspicious = []
        
        # Check for non-ASCII characters
        try:
            url.encode('ascii')
        except UnicodeEncodeError:
            suspicious.append("Non-ASCII characters")
        
        # Check for control characters
        if any(ord(c) < 32 for c in url):
            suspicious.append("Control characters")
        
        # Check for multiple consecutive special characters
        if re.search(r'[!@#$%^&*]{2,}', url):
            suspicious.append("Multiple consecutive special characters")
        
        return suspicious
    
    def _check_certificate_validity(self, domain: str) -> bool:
        """Check if certificate is valid (simulated)"""
        # In production, perform actual SSL/TLS certificate validation
        return True
    
    def _check_canonical_tag(self, url: str) -> bool:
        """Check for canonical tag (simulated)"""
        return True
    
    def _check_robots_meta(self, url: str) -> bool:
        """Check for robots meta tag (simulated)"""
        return True
    
    def _check_og_tags(self, url: str) -> bool:
        """Check for Open Graph tags (simulated)"""
        return True
    
    def _check_structured_data(self, url: str) -> bool:
        """Check for structured data (Schema.org) (simulated)"""
        return True
    
    def _detect_content_type(self, url: str) -> Optional[str]:
        """Detect content type from URL"""
        if url.endswith('.pdf'):
            return ContentType.PDF.value
        elif any(url.endswith(ext) for ext in ['.jpg', '.png', '.gif', '.webp']):
            return ContentType.IMAGE.value
        elif url.endswith('.json'):
            return ContentType.JSON.value
        elif url.endswith('.xml'):
            return ContentType.XML.value
        else:
            return ContentType.HTML.value
    
    def _check_responsive_design(self, url: str) -> bool:
        """Check for responsive design (simulated)"""
        return True
    
    def _estimate_response_time(self, domain: str) -> float:
        """Estimate response time (simulated)"""
        return 100.0
    
    def _check_cdn_usage(self, domain: str) -> bool:
        """Check for CDN usage (simulated)"""
        cdn_providers = ['cloudflare', 'akamai', 'cloudfront', 'fastly', 'maxcdn']
        return any(cdn in domain.lower() for cdn in cdn_providers)
    
    def _check_gdpr_compliance(self, url: str) -> bool:
        """Check for GDPR compliance (simulated)"""
        return True
    
    def _check_ccpa_compliance(self, url: str) -> bool:
        """Check for CCPA compliance (simulated)"""
        return True
    
    def _check_cookie_policy(self, url: str) -> bool:
        """Check for cookie policy (simulated)"""
        return True
    
    def _check_privacy_policy(self, url: str) -> bool:
        """Check for privacy policy (simulated)"""
        return True
    
    def _check_mobile_friendly(self, url: str) -> bool:
        """Check for mobile friendly design (simulated)"""
        return True
    
    def _check_safe_browsing(self, domain: str) -> bool:
        """Check against safe browsing lists (simulated)"""
        return True
    
    def batch_validate(self, urls: List[str]) -> List[URLValidationResult]:
        """
        Validate multiple URLs
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            List of validation results
        """
        return [self.validate_url(url) for url in urls]
    
    def export_results(self, output_format: str = 'json') -> str:
        """
        Export validation results
        
        Args:
            output_format: 'json' or 'csv'
            
        Returns:
            Formatted results string
        """
        if output_format == 'json':
            results_dict = {
                url: asdict(result) 
                for url, result in self.validation_results.items()
            }
            return json.dumps(results_dict, indent=2, default=str)
        elif output_format == 'csv':
            # Implement CSV export
            lines = []
            if self.validation_results:
                # Header
                first_result = list(self.validation_results.values())[0]
                headers = list(asdict(first_result).keys())
                lines.append(','.join(headers))
                
                # Data rows
                for result in self.validation_results.values():
                    values = [str(getattr(result, key)).replace(',', ';') 
                             for key in headers]
                    lines.append(','.join(values))
            
            return '\n'.join(lines)
        
        return ""
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all validations"""
        if not self.validation_results:
            return {}
        
        results = list(self.validation_results.values())
        total = len(results)
        valid_count = sum(1 for r in results if r.is_valid)
        https_count = sum(1 for r in results if r.is_https)
        secure_count = sum(1 for r in results if r.is_secure)
        
        avg_phishing_risk = sum(r.phishing_risk_score for r in results) / total
        avg_malware_risk = sum(r.malware_risk_score for r in results) / total
        avg_spam_risk = sum(r.spam_risk_score for r in results) / total
        
        return {
            'total_urls': total,
            'valid_urls': valid_count,
            'invalid_urls': total - valid_count,
            'https_urls': https_count,
            'secure_urls': secure_count,
            'average_phishing_risk': round(avg_phishing_risk, 3),
            'average_malware_risk': round(avg_malware_risk, 3),
            'average_spam_risk': round(avg_spam_risk, 3),
            'unique_domains': len(set(r.domain for r in results)),
            'validation_timestamp': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }


# Example usage
if __name__ == "__main__":
    # Initialize validator
    validator = URLValidator()
    
    # Example 1: Extract URLs from text
    sample_text = """
    Check out our website at https://www.example.com and https://shop.example.org
    You can also visit http://192.168.1.1:8080/admin or www.another-site.net
    """
    
    print("=" * 80)
    print("URL EXTRACTION RESULTS")
    print("=" * 80)
    extracted = validator.extract_urls_from_text(sample_text)
    for url in extracted:
        print(f"  • {url}")
    
    # Example 2: Validate individual URLs
    test_urls = [
        "https://www.example.com/path/to/page?param1=value1&param2=value2",
        "http://subdomain.example.org:8080/",
        "ftp://files.example.net/documents",
        "https://192.168.1.1/admin",
        "http://bit.ly/shortened"
    ]
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE URL VALIDATION RESULTS")
    print("=" * 80)
    
    for url in test_urls:
        result = validator.validate_url(url)
        print(f"\nURL: {result.url}")
        print(f"  Valid: {result.is_valid}")
        print(f"  Normalized: {result.normalized_url}")
        print(f"  Scheme: {result.scheme}")
        print(f"  Domain: {result.domain}")
        print(f"  Path: {result.path}")
        print(f"  Is HTTPS: {result.is_https}")
        print(f"  Is Secure: {result.is_secure}")
        print(f"  Phishing Risk: {result.phishing_risk_score:.2%}")
        print(f"  Malware Risk: {result.malware_risk_score:.2%}")
        print(f"  Spam Risk: {result.spam_risk_score:.2%}")
        print(f"  Mobile Friendly: {result.mobile_friendly}")
        print(f"  Safe Browsing: {result.safe_browsing}")
        if result.validation_errors:
            print(f"  Errors: {', '.join(result.validation_errors)}")
    
    # Example 3: Batch validation
    print("\n" + "=" * 80)
    print("BATCH VALIDATION SUMMARY")
    print("=" * 80)
    batch_results = validator.batch_validate(test_urls)
    summary = validator.get_validation_summary()
    
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Example 4: Export results
    print("\n" + "=" * 80)
    print("JSON EXPORT (First 500 chars)")
    print("=" * 80)
    json_export = validator.export_results('json')
    print(json_export[:500] + "...")
