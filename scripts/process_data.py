"""
Data Processing Script for Australian Bureau of Statistics (ABS) Excel Files
Processes household spending, housing costs, and income/work data
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

class ABSDataProcessor:
    def __init__(self, input_folder='../dataset', output_folder='../processed'):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.ensure_output_folder()
    
    def ensure_output_folder(self):
        """Ensure output folder exists"""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def process_household_spending(self):
        """Process household spending data"""
        print("Processing household spending data...")
        
        # Read the file
        df = pd.read_excel(f'{self.input_folder}/household_spending.xlsx')
        
        # Find data start (after headers)
        data_start_row = None
        for i, row in df.iterrows():
            if str(row.iloc[0]).startswith('Data Item Description'):
                data_start_row = i + 2  # Skip header row and empty row
                break
        
        if data_start_row is None:
            print("Could not find data start in household spending file")
            return {}
        
        # Extract column names from header row
        header_row = df.iloc[data_start_row - 2]
        columns = [str(col) for col in header_row.values if str(col) != 'nan']
        
        # Process data rows
        spending_data = []
        for i in range(data_start_row, len(df)):
            row = df.iloc[i]
            if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                continue
                
            spending_item = {
                'description': str(row.iloc[0]),
                'series_type': str(row.iloc[3]) if not pd.isna(row.iloc[3]) else None,
                'series_id': str(row.iloc[4]) if not pd.isna(row.iloc[4]) else None,
                'series_start': row.iloc[5] if not pd.isna(row.iloc[5]) else None,
                'series_end': row.iloc[6] if not pd.isna(row.iloc[6]) else None,
                'observations': row.iloc[7] if not pd.isna(row.iloc[7]) else None,
                'unit': str(row.iloc[8]) if not pd.isna(row.iloc[8]) else None,
                'data_type': str(row.iloc[9]) if not pd.isna(row.iloc[9]) else None,
                'frequency': str(row.iloc[10]) if not pd.isna(row.iloc[10]) else None,
                'collection_month': row.iloc[11] if not pd.isna(row.iloc[11]) else None
            }
            
            # Convert datetime objects to strings
            if isinstance(spending_item['series_start'], datetime):
                spending_item['series_start'] = spending_item['series_start'].strftime('%Y-%m-%d')
            if isinstance(spending_item['series_end'], datetime):
                spending_item['series_end'] = spending_item['series_end'].strftime('%Y-%m-%d')
            
            spending_data.append(spending_item)
        
        # Calculate aggregated statistics
        total_observations = sum([item['observations'] for item in spending_data if item['observations']])
        unique_categories = len(set([item['description'].split(';')[1].strip() for item in spending_data if ';' in item['description']]))
        
        # Extract spending categories
        categories = {}
        for item in spending_data:
            if ';' in item['description']:
                parts = item['description'].split(';')
                if len(parts) >= 2:
                    category = parts[1].strip()
                    if category not in categories:
                        categories[category] = {
                            'count': 0,
                            'total_observations': 0,
                            'series_ids': []
                        }
                    categories[category]['count'] += 1
                    if item['observations']:
                        categories[category]['total_observations'] += item['observations']
                    if item['series_id']:
                        categories[category]['series_ids'].append(item['series_id'])
        
        result = {
            'metadata': {
                'source': 'Australian Bureau of Statistics - Monthly Household Spending Indicator',
                'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_series': len(spending_data),
                'total_observations': total_observations,
                'unique_categories': unique_categories,
                'data_period': f"2019-2025 (estimated based on series data)"
            },
            'summary_statistics': {
                'categories_breakdown': categories,
                'most_observed_category': max(categories.items(), key=lambda x: x[1]['total_observations'])[0] if categories else None,
                'average_observations_per_series': total_observations / len(spending_data) if spending_data else 0
            },
            'detailed_data': spending_data
        }
        
        return result
    
    def process_housing_costs(self):
        """Process housing costs data"""
        print("Processing housing costs data...")
        
        # This appears to be a contents/index page, let's extract what we can
        df = pd.read_excel(f'{self.input_folder}/housing_cost.xlsx')
        
        # Extract table information
        tables_info = []
        for i, row in df.iterrows():
            if not pd.isna(row.iloc[1]) and str(row.iloc[1]).replace('.', '').isdigit():
                table_number = row.iloc[1]
                table_description = str(row.iloc[2]) if not pd.isna(row.iloc[2]) else 'No description'
                tables_info.append({
                    'table_number': float(table_number),
                    'description': table_description
                })
        
        result = {
            'metadata': {
                'source': 'Australian Bureau of Statistics - Housing Occupancy and Costs, Australia, 2019–20',
                'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'release_date': 'Released at 11:30 am (CANBERRA TIME) 25 May 2022',
                'data_period': '2019-20',
                'note': 'This appears to be a table of contents file. Actual housing cost data would be in separate worksheets or files.'
            },
            'available_tables': tables_info,
            'summary_statistics': {
                'total_tables_available': len(tables_info),
                'focus_area': 'Housing Costs as a Proportion of Income'
            }
        }
        
        return result
    
    def process_income_work(self):
        """Process income and work data"""
        print("Processing income and work data...")
        
        df = pd.read_excel(f'{self.input_folder}/income_work.xlsx')
        
        # Extract table information
        tables_info = []
        for i, row in df.iterrows():
            if not pd.isna(row.iloc[1]) and str(row.iloc[1]).replace('.', '').isdigit():
                table_number = row.iloc[1]
                table_description = str(row.iloc[2]) if not pd.isna(row.iloc[2]) else 'No description'
                tables_info.append({
                    'table_number': int(float(table_number)),
                    'description': table_description
                })
        
        # Categorize tables by topic
        income_tables = [t for t in tables_info if 'income' in t['description'].lower()]
        employment_tables = [t for t in tables_info if any(word in t['description'].lower() for word in ['employment', 'employed', 'labour', 'industry', 'occupation'])]
        demographic_tables = [t for t in tables_info if any(word in t['description'].lower() for word in ['age', 'sex', 'composition', 'territory', 'state'])]
        
        result = {
            'metadata': {
                'source': 'Australian Bureau of Statistics - Census of Population and Housing: Income and work data summary, 2021',
                'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'release_date': 'Released at 11:30am (Canberra time) 12 October 2022',
                'data_period': '2021 Census',
                'note': 'This appears to be a table of contents file. Actual data would be in separate worksheets or files.'
            },
            'available_tables': tables_info,
            'summary_statistics': {
                'total_tables_available': len(tables_info),
                'income_focused_tables': len(income_tables),
                'employment_focused_tables': len(employment_tables),
                'demographic_analysis_tables': len(demographic_tables)
            },
            'categorized_tables': {
                'income_analysis': income_tables,
                'employment_analysis': employment_tables,
                'demographic_analysis': demographic_tables
            }
        }
        
        return result
    
    def generate_cross_dataset_analysis(self, household_data, housing_data, income_data):
        """Generate correlations and insights across datasets"""
        print("Generating cross-dataset analysis...")
        
        analysis = {
            'metadata': {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'datasets_analyzed': ['household_spending', 'housing_costs', 'income_work']
            },
            'temporal_analysis': {
                'household_spending_period': household_data['metadata']['data_period'],
                'housing_costs_period': housing_data['metadata']['data_period'],
                'income_work_period': income_data['metadata']['data_period'],
                'note': 'Different time periods may affect direct correlations'
            },
            'thematic_connections': {
                'housing_expenditure_categories': [
                    cat for cat in household_data['summary_statistics']['categories_breakdown'].keys()
                    if any(word in cat.lower() for word in ['housing', 'rent', 'mortgage', 'utilities'])
                ],
                'potential_income_correlations': [
                    'Household spending patterns may correlate with income levels from Census 2021',
                    'Housing costs as proportion of income (2019-20) can be compared with spending patterns',
                    'Geographic variations in income may explain regional spending differences'
                ],
                'research_opportunities': [
                    'Compare household spending categories with housing cost proportions',
                    'Analyze discretionary vs non-discretionary spending against income levels',
                    'Study temporal trends in spending vs housing affordability'
                ]
            },
            'data_quality_assessment': {
                'household_spending': {
                    'completeness': 'High - detailed time series data',
                    'granularity': 'Monthly data with category breakdowns',
                    'limitations': 'Recent data, may not align with Census timing'
                },
                'housing_costs': {
                    'completeness': 'Index only - requires additional data files',
                    'granularity': 'Household characteristic breakdowns available',
                    'limitations': '2019-20 period, pre-COVID impact'
                },
                'income_work': {
                    'completeness': 'Index only - requires additional data files',
                    'granularity': 'Demographic and geographic breakdowns',
                    'limitations': '2021 Census - point-in-time snapshot'
                }
            }
        }
        
        return analysis
    
    def save_json(self, data, filename):
        """Save data to JSON file"""
        filepath = os.path.join(self.output_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"Saved {filename}")
    
    def process_all_data(self):
        """Process all datasets and generate comprehensive analysis"""
        print("Starting comprehensive data processing...")
        print("=" * 50)
        
        # Process each dataset
        household_data = self.process_household_spending()
        housing_data = self.process_housing_costs()
        income_data = self.process_income_work()
        
        # Generate cross-dataset analysis
        cross_analysis = self.generate_cross_dataset_analysis(household_data, housing_data, income_data)
        
        # Save individual datasets
        self.save_json(household_data, 'household_spending.json')
        self.save_json(housing_data, 'housing_costs.json')
        self.save_json(income_data, 'income_work.json')
        
        # Save cross-analysis
        self.save_json(cross_analysis, 'cross_dataset_analysis.json')
        
        # Generate summary report
        summary = {
            'processing_summary': {
                'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'datasets_processed': 4,
                'files_generated': [
                    'household_spending.json',
                    'housing_costs.json', 
                    'income_work.json',
                    'cross_dataset_analysis.json'
                ]
            },
            'key_findings': {
                'household_spending': {
                    'total_series': household_data['metadata']['total_series'],
                    'categories': len(household_data['summary_statistics']['categories_breakdown']),
                    'time_span': household_data['metadata']['data_period']
                },
                'housing_costs': {
                    'tables_available': housing_data['summary_statistics']['total_tables_available'],
                    'focus': housing_data['summary_statistics']['focus_area']
                },
                'income_work': {
                    'tables_available': income_data['summary_statistics']['total_tables_available'],
                    'income_tables': income_data['summary_statistics']['income_focused_tables'],
                    'employment_tables': income_data['summary_statistics']['employment_focused_tables']
                }
            },
            'next_steps': [
                'Access individual table sheets within Excel files for detailed data',
                'Develop visualization dashboard using processed JSON data',
                'Conduct time-series analysis on household spending trends',
                'Perform correlation analysis between income and spending patterns',
                'Create geographic analysis combining all datasets'
            ]
        }
        
        self.save_json(summary, 'processing_summary.json')
        
        print("=" * 50)
        print("Data processing completed successfully!")
        print(f"Generated {len(summary['processing_summary']['files_generated']) + 1} JSON files in {self.output_folder}")
        
        return summary

def main():
    """Main execution function"""
    processor = ABSDataProcessor()
    summary = processor.process_all_data()
    
    print("\nProcessing Summary:")
    print(f"- Processed {summary['key_findings']['household_spending']['total_series']} household spending series")
    print(f"- Identified {summary['key_findings']['household_spending']['categories']} spending categories") 
    print(f"- Found {summary['key_findings']['housing_costs']['tables_available']} housing cost tables")
    print(f"- Found {summary['key_findings']['income_work']['tables_available']} income/work tables")
    print(f"\nAll processed data saved to JSON files for visualization and further analysis.")

if __name__ == "__main__":
    main()
