"""
Tests for database utility functions

Tests cover:
- Database connection
- User queries
- Loan queries (single and multiple)
- Error handling
"""

import pytest

from src.utils.database import (
    get_db_connection,
    get_user_by_username,
    get_user_by_id,
    get_loan_by_id,
    get_loans_by_user_id,
)


class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_get_db_connection_returns_connection(self):
        """Test that we can get a valid database connection"""
        conn = get_db_connection()
        assert conn is not None
        conn.close()
    
    def test_connection_has_row_factory(self):
        """Test that connection has row_factory set for dict access"""
        conn = get_db_connection()
        assert conn.row_factory is not None
        conn.close()


class TestUserQueries:
    """Test user-related database queries"""
    
    def test_get_user_by_username_existing_user(self):
        """Test retrieving user by username for authentication"""
        user = get_user_by_username('alice')
        
        assert user is not None
        assert user['user_id'] == 'usr_alice'
        assert user['username'] == 'alice'
        assert user['first_name'] == 'Alice'
        assert user['last_name'] == 'Johnson'
        assert user['customer_type'] == 'retail'
        assert 'password' in user  # Password included for authentication
    
    def test_get_user_by_username_nonexistent(self):
        """Test retrieving non-existent username returns None"""
        user = get_user_by_username('nonexistent')
        assert user is None
    
    def test_get_user_by_username_case_sensitive(self):
        """Test that username lookup is case-sensitive"""
        user = get_user_by_username('ALICE')
        assert user is None  # Case-sensitive, so 'ALICE' != 'alice'
        
        user = get_user_by_username('alice')
        assert user is not None
    
    def test_get_user_by_id_existing_user(self):
        """Test retrieving user by ID (for general lookups)"""
        user = get_user_by_id('usr_alice')
        
        assert user is not None
        assert user['user_id'] == 'usr_alice'
        assert user['username'] == 'alice'
        assert user['first_name'] == 'Alice'
        assert user['last_name'] == 'Johnson'
        assert user['customer_type'] == 'retail'
        assert 'password' not in user  # Password excluded for security
    
    def test_get_user_by_id_nonexistent(self):
        """Test retrieving non-existent user ID returns None"""
        user = get_user_by_id('usr_nonexistent')
        assert user is None
    
    def test_get_corporate_user(self):
        """Test retrieving a corporate customer"""
        user = get_user_by_username('charlie')
        
        assert user is not None
        assert user['first_name'] == 'Charlie'
        assert user['last_name'] == 'Williams'
        assert user['customer_type'] == 'corporate'


class TestLoanQueries:
    """Test loan-related database queries"""
    
    def test_get_loan_by_id_existing_loan(self):
        """Test retrieving an existing loan returns all fields"""
        loan = get_loan_by_id('LN-101')
        
        assert loan is not None
        assert loan['loan_id'] == 'LN-101'
        assert loan['user_id'] == 'usr_alice'
        assert loan['customer_type'] == 'retail'
        assert loan['balance'] == 18500.0
        assert loan['interest_rate'] == 7.5
        assert loan['maturity_date'] == '2028-06-15'
        assert loan['status'] == 'Active'
    
    def test_get_loan_by_id_nonexistent_loan(self):
        """Test retrieving non-existent loan returns None"""
        loan = get_loan_by_id('LN-999')
        assert loan is None
    
    def test_get_loan_corporate_loan(self):
        """Test retrieving a corporate loan"""
        loan = get_loan_by_id('LN-301')
        
        assert loan is not None
        assert loan['customer_type'] == 'corporate'
        assert loan['balance'] == 2500000.0
        assert loan['interest_rate'] == 4.5


class TestMultipleLoanQueries:
    """Test queries that return multiple loans"""
    
    def test_get_loans_by_user_id_multiple_loans(self):
        """Test retrieving multiple loans for a user"""
        loans = get_loans_by_user_id('usr_bob')
        
        assert len(loans) == 3
        assert all(loan['user_id'] == 'usr_bob' for loan in loans)
        assert all(loan['customer_type'] == 'retail' for loan in loans)
    
    def test_get_loans_by_user_id_single_loan_user(self):
        """Test user with multiple loans (Alice has 2)"""
        loans = get_loans_by_user_id('usr_alice')
        
        assert len(loans) == 2
        loan_ids = [loan['loan_id'] for loan in loans]
        assert 'LN-101' in loan_ids
        assert 'LN-102' in loan_ids
    
    def test_get_loans_by_user_id_nonexistent_user(self):
        """Test that non-existent user returns empty list"""
        loans = get_loans_by_user_id('usr_nonexistent')
        assert loans == []
    
    def test_loans_include_all_fields(self):
        """Test that loan queries return all expected fields"""
        loans = get_loans_by_user_id('usr_alice')
        
        required_fields = [
            'loan_id', 'user_id', 'customer_type', 
            'balance', 'interest_rate', 'maturity_date', 'status'
        ]
        
        for loan in loans:
            for field in required_fields:
                assert field in loan, f"Missing field: {field}"


class TestDataIntegrity:
    """Test data relationships and integrity"""
    
    def test_total_loan_balance_retail_user(self):
        """Test calculating total balance for retail user stays under limit"""
        loans = get_loans_by_user_id('usr_bob')
        total = sum(loan['balance'] for loan in loans)
        
        # Retail limit is $100,000
        assert total == 87000.0
        assert total < 100000.0
    
    def test_total_loan_balance_corporate_user(self):
        """Test calculating total balance for corporate user"""
        loans = get_loans_by_user_id('usr_diana')
        total = sum(loan['balance'] for loan in loans)
        
        # Corporate limit is $10,000,000
        assert total == 9400000.0
        assert total < 10000000.0
    
    def test_interest_rates_in_reasonable_range(self):
        """Test that interest rates are realistic (0-20%)"""
        # Get all loans for all users
        all_user_ids = ['usr_alice', 'usr_bob', 'usr_charlie', 'usr_diana']
        
        for user_id in all_user_ids:
            loans = get_loans_by_user_id(user_id)
            for loan in loans:
                assert 0 < loan['interest_rate'] < 20, \
                    f"Unrealistic interest rate: {loan['interest_rate']}"
    
    def test_retail_rates_higher_than_corporate(self):
        """Test that retail rates are generally higher than corporate"""
        retail_loans = get_loans_by_user_id('usr_alice')
        corporate_loans = get_loans_by_user_id('usr_charlie')
        
        avg_retail = sum(l['interest_rate'] for l in retail_loans) / len(retail_loans)
        avg_corporate = sum(l['interest_rate'] for l in corporate_loans) / len(corporate_loans)
        
        assert avg_retail > avg_corporate, \
            "Retail rates should be higher than corporate rates"
