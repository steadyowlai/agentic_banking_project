"""
Tests for file utility functions

Tests cover:
- Reading policy files
- Error handling for missing files
- File content validation
"""

import pytest
import os

from src.utils.file_utils import get_policy_content


class TestPolicyFileReading:
    """Test reading policy document files"""
    
    def test_get_retail_policy_content(self):
        """Test reading retail policy returns content"""
        content = get_policy_content('retail')
        
        assert content is not None
        assert len(content) > 0
        assert 'Retail' in content
        assert '$100,000' in content or '100,000' in content
    
    def test_get_corporate_policy_content(self):
        """Test reading corporate policy returns content"""
        content = get_policy_content('corporate')
        
        assert content is not None
        assert len(content) > 0
        assert 'Corporate' in content
        assert '$10,000,000' in content or '10,000,000' in content
    
    def test_get_policy_case_insensitive(self):
        """Test that customer_type is case-insensitive"""
        content_lower = get_policy_content('retail')
        content_upper = get_policy_content('RETAIL')
        content_mixed = get_policy_content('Retail')
        
        assert content_lower == content_upper == content_mixed
    
    def test_get_nonexistent_policy(self):
        """Test that requesting non-existent policy returns None"""
        content = get_policy_content('nonexistent')
        assert content is None
    
    def test_invalid_policy_type(self):
        """Test handling of invalid policy types"""
        content = get_policy_content('premium')  # Not a valid type
        assert content is None


class TestPolicyContentValidation:
    """Test that policy content is valid and complete"""
    
    def test_retail_policy_mentions_limit(self):
        """Test that retail policy mentions the borrowing limit"""
        content = get_policy_content('retail')
        
        # Should mention the $100k limit
        assert '100,000' in content or '100k' in content.lower()
    
    def test_corporate_policy_mentions_limit(self):
        """Test that corporate policy mentions the borrowing limit"""
        content = get_policy_content('corporate')
        
        # Should mention the $10M limit
        assert '10,000,000' in content or '10m' in content.lower()
    
    def test_policy_not_empty(self):
        """Test that policies are not empty files"""
        retail = get_policy_content('retail')
        corporate = get_policy_content('corporate')
        
        assert len(retail) > 50, "Retail policy seems too short"
        assert len(corporate) > 50, "Corporate policy seems too short"
    
    def test_policies_are_different(self):
        """Test that retail and corporate policies are different"""
        retail = get_policy_content('retail')
        corporate = get_policy_content('corporate')
        
        assert retail != corporate, "Policies should have different content"


class TestPolicyFileStructure:
    """Test the underlying file structure assumptions"""
    
    def test_policy_files_exist(self):
        """Test that policy files physically exist on disk"""
        # This tests the file system, not just the function
        import os
        from src.utils.file_utils import POLICY_DIR
        
        retail_path = os.path.join(POLICY_DIR, 'retail_policy.txt')
        corporate_path = os.path.join(POLICY_DIR, 'corporate_policy.txt')
        
        assert os.path.exists(retail_path), f"Retail policy not found at {retail_path}"
        assert os.path.exists(corporate_path), f"Corporate policy not found at {corporate_path}"
    
    def test_policy_files_are_readable(self):
        """Test that policy files have read permissions"""
        import os
        from src.utils.file_utils import POLICY_DIR
        
        retail_path = os.path.join(POLICY_DIR, 'retail_policy.txt')
        corporate_path = os.path.join(POLICY_DIR, 'corporate_policy.txt')
        
        assert os.access(retail_path, os.R_OK), "Cannot read retail policy file"
        assert os.access(corporate_path, os.R_OK), "Cannot read corporate policy file"
