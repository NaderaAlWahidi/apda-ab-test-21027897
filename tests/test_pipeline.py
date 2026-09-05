import pytest
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
 
# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
 
from pipeline import (
    validate_data_contract,
    clean_data,
    load_data,
    inspect_data
)
 
 
# FIXTURES: Create test data
 
@pytest.fixture
def valid_data():
    #Create a valid test dataset.
    return pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5],
        'timestamp': [
            '2017-01-02 10:00:00',
            '2017-01-02 11:00:00',
            '2017-01-03 10:00:00',
            '2017-01-03 11:00:00',
            '2017-01-04 10:00:00'
        ],
        'group': ['control', 'treatment', 'control', 'treatment', 'control'],
        'landing_page': ['old_page', 'new_page', 'old_page', 'new_page', 'old_page'],
        'converted': [0, 1, 1, 0, 1]
    })
 
 
@pytest.fixture
def data_with_missing_column():
    #Create a dataset with missing required column.
    return pd.DataFrame({
        'user_id': [1, 2, 3],
        'timestamp': ['2017-01-02 10:00:00', '2017-01-02 11:00:00', '2017-01-03 10:00:00'],
        'group': ['control', 'treatment', 'control'],
        # Missing 'landing_page' column
        'converted': [0, 1, 1]
    })
 
 
@pytest.fixture
def data_with_misaligned_assignments():
    #Create a dataset with incorrect group/page alignment.
    return pd.DataFrame({
        'user_id': [1, 2, 3, 4],
        'timestamp': [
            '2017-01-02 10:00:00',
            '2017-01-02 11:00:00',
            '2017-01-03 10:00:00',
            '2017-01-03 11:00:00'
        ],
        'group': ['control', 'treatment', 'control', 'treatment'],
        'landing_page': ['old_page', 'new_page', 'new_page', 'old_page'],  # Rows 2 and 3 misaligned
        'converted': [0, 1, 1, 0]
    })
 
 
@pytest.fixture
def data_with_duplicate_user():
    #Create a dataset with duplicate user IDs.
    return pd.DataFrame({
        'user_id': [1, 2, 2, 3],  # user_id 2 appears twice
        'timestamp': [
            '2017-01-02 10:00:00',
            '2017-01-02 11:00:00',  # First appearance (earlier)
            '2017-01-02 12:00:00',  # Second appearance (later)
            '2017-01-03 10:00:00'
        ],
        'group': ['control', 'treatment', 'treatment', 'control'],
        'landing_page': ['old_page', 'new_page', 'new_page', 'old_page'],
        'converted': [0, 1, 0, 1]  # Different conversion values
    })
 
 
@pytest.fixture
def data_with_invalid_group_value():
    #Create a dataset with invalid group value.
    return pd.DataFrame({
        'user_id': [1, 2, 3],
        'timestamp': ['2017-01-02 10:00:00', '2017-01-02 11:00:00', '2017-01-03 10:00:00'],
        'group': ['control', 'invalid_group', 'control'],  # 'invalid_group' not allowed
        'landing_page': ['old_page', 'new_page', 'old_page'],
        'converted': [0, 1, 1]
    })
 
 
@pytest.fixture
def data_with_invalid_converted_value():
    #Create a dataset with invalid converted value.
    return pd.DataFrame({
        'user_id': [1, 2, 3],
        'timestamp': ['2017-01-02 10:00:00', '2017-01-02 11:00:00', '2017-01-03 10:00:00'],
        'group': ['control', 'treatment', 'control'],
        'landing_page': ['old_page', 'new_page', 'old_page'],
        'converted': [0, 2, 1]  # 2 is not valid (only 0 or 1)
    })
 
 
# TESTS: Validation
 
class TestValidation:
    #Tests for data contract validation.
    
    def test_validation_passes_with_valid_data(self, valid_data):
        #Test that validation passes with valid data.
        # Should not raise any exception
        validate_data_contract(valid_data)
    
    def test_validation_rejects_missing_required_column(self, data_with_missing_column):
        #Test that validation rejects missing required column.
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_data_contract(data_with_missing_column)
    
    def test_validation_rejects_invalid_group_value(self, data_with_invalid_group_value):
        #Test that validation rejects invalid group values.
        with pytest.raises(ValueError, match="Invalid group values"):
            validate_data_contract(data_with_invalid_group_value)
    
    def test_validation_rejects_invalid_converted_value(self, data_with_invalid_converted_value):
        #Test that validation rejects invalid converted values.
        with pytest.raises(ValueError, match="Invalid converted values"):
            validate_data_contract(data_with_invalid_converted_value)
 
 
# TESTS: Cleaning
 
class TestCleaning:
    #Tests for data cleaning and deduplication.
    
    def test_cleaning_removes_misaligned_assignments(self, data_with_misaligned_assignments):
        #Test that cleaning removes incorrect group/page assignments.
        # Original data has 4 rows: rows 2 and 3 are misaligned
        assert len(data_with_misaligned_assignments) == 4
        
        cleaned, report = clean_data(data_with_misaligned_assignments)
        
        # Should remove 2 rows (misaligned records)
        assert len(cleaned) == 2
        assert report['rows_removed_by_alignment'] == 2
        
        # Verify remaining records are correctly aligned
        assert all((cleaned['group'] == 'control') & (cleaned['landing_page'] == 'old_page') |
                   (cleaned['group'] == 'treatment') & (cleaned['landing_page'] == 'new_page'))
    
    def test_cleaning_keeps_earliest_record_for_duplicate_user(self, data_with_duplicate_user):
        #Test that cleaning keeps only the earliest record for duplicate user IDs.
        # Original data has 4 rows, but user_id 2 appears twice
        assert len(data_with_duplicate_user) == 4
        assert data_with_duplicate_user['user_id'].duplicated().sum() == 1
        
        cleaned, report = clean_data(data_with_duplicate_user)
        
        # Should have 3 unique records
        assert len(cleaned) == 3
        assert report['rows_removed_by_deduplication'] == 1
        assert report['all_user_ids_unique'] is True
        
        # Verify that the earlier record for user_id 2 was kept
        user_2_record = cleaned[cleaned['user_id'] == 2].iloc[0]
        assert user_2_record['timestamp'] == pd.to_datetime('2017-01-02 11:00:00')
        assert user_2_record['converted'] == 1  # From first appearance
    
    def test_cleaning_preserves_original_dataframe(self, valid_data):
        #Test that cleaning does not modify the original DataFrame.
        original_copy = valid_data.copy()
        
        # Call clean_data
        cleaned, report = clean_data(valid_data)
        
        # Verify original is unchanged
        pd.testing.assert_frame_equal(valid_data, original_copy)
    
    def test_cleaning_creates_experiment_date(self, valid_data):
        #Test that cleaning creates experiment_date column.
        cleaned, report = clean_data(valid_data)
        
        # Should have experiment_date column
        assert 'experiment_date' in cleaned.columns
        
        # Should be date type
        assert cleaned['experiment_date'].dtype == object or pd.api.types.is_datetime64_any_dtype(cleaned['experiment_date'])
    
    def test_cleaning_converts_timestamp_to_datetime(self, valid_data):
        #Test that cleaning converts timestamp to datetime.
        cleaned, report = clean_data(valid_data)
        
        # timestamp should be datetime type
        assert pd.api.types.is_datetime64_any_dtype(cleaned['timestamp'])
    
    def test_cleaning_sorts_by_timestamp(self, data_with_duplicate_user):
        #Test that cleaning sorts records by timestamp.
        cleaned, report = clean_data(data_with_duplicate_user)
        
        # Verify timestamps are sorted
        timestamps = pd.to_datetime(cleaned['timestamp']).values
        assert all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
 
 
# TESTS: Integration
 
class TestIntegration:
    #Integration tests for the full pipeline.
    
    #Test full pipeline with valid data
    def test_full_pipeline_valid_data(self, valid_data):
        # Validate should pass
        validate_data_contract(valid_data)
        
        # Cleaning should succeed
        cleaned, report = clean_data(valid_data)
        
        # Should have cleaned data
        assert len(cleaned) > 0
        assert report['all_user_ids_unique'] is True
    
    def test_cleaning_report_contains_required_metrics(self, valid_data):
        #Test that cleaning report contains all required metrics.
        cleaned, report = clean_data(valid_data)
        
        required_metrics = [
            'initial_rows',
            'rows_after_alignment_cleaning',
            'rows_removed_by_alignment',
            'rows_after_deduplication',
            'rows_removed_by_deduplication',
            'final_rows',
            'unique_user_ids',
            'all_user_ids_unique'
        ]
        
        for metric in required_metrics:
            assert metric in report, f"Missing metric: {metric}"
    
    def test_row_count_consistency(self, data_with_misaligned_assignments, data_with_duplicate_user):
        #Test that row count calculations are consistent.
        cleaned, report = clean_data(data_with_misaligned_assignments)
        
        # Verify row count math
        total_removed = report['rows_removed_by_alignment'] + report['rows_removed_by_deduplication']
        expected_final = report['initial_rows'] - total_removed
        
        assert report['final_rows'] == expected_final
        assert report['final_rows'] == len(cleaned)
 
 
# TESTS: Edge Cases
 
class TestEdgeCases:
    #Tests for edge cases and boundary conditions.
    
    def test_single_record_dataset(self):
        """Test cleaning with only one record."""
        data = pd.DataFrame({
            'user_id': [1],
            'timestamp': ['2017-01-02 10:00:00'],
            'group': ['control'],
            'landing_page': ['old_page'],
            'converted': [1]
        })
        
        cleaned, report = clean_data(data)
        
        assert len(cleaned) == 1
        assert report['final_rows'] == 1
    
    def test_all_records_misaligned(self):
        """Test cleaning when all records are misaligned."""
        data = pd.DataFrame({
            'user_id': [1, 2, 3],
            'timestamp': ['2017-01-02 10:00:00', '2017-01-02 11:00:00', '2017-01-03 10:00:00'],
            'group': ['control', 'treatment', 'control'],
            'landing_page': ['new_page', 'old_page', 'new_page'],  # All misaligned
            'converted': [0, 1, 1]
        })
        
        cleaned, report = clean_data(data)
        
        assert len(cleaned) == 0
        assert report['rows_removed_by_alignment'] == 3
 
 
# Run tests

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 