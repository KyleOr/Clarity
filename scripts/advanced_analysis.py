"""
Advanced Statistical Analysis Script
Performs deeper analysis on the processed ABS data
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import os

class AdvancedAnalyzer:
    def __init__(self, processed_folder='../processed'):
        self.processed_folder = processed_folder
        self.load_processed_data()
    
    def load_processed_data(self):
        """Load all processed JSON files"""
        print("Loading processed data...")
        
        with open(f'{self.processed_folder}/household_spending.json', 'r', encoding='utf-8') as f:
            self.household_data = json.load(f)
        
        with open(f'{self.processed_folder}/housing_costs.json', 'r', encoding='utf-8') as f:
            self.housing_data = json.load(f)
        
        with open(f'{self.processed_folder}/income_work.json', 'r', encoding='utf-8') as f:
            self.income_data = json.load(f)
        
        print("Data loaded successfully.")
    
    def analyze_spending_patterns(self):
        """Perform detailed analysis of spending patterns"""
        print("Analyzing spending patterns...")
        
        categories = self.household_data['summary_statistics']['categories_breakdown']
        
        # Calculate category statistics
        category_stats = {}
        for category, data in categories.items():
            category_stats[category] = {
                'series_count': data['count'],
                'total_observations': data['total_observations'],
                'avg_observations_per_series': data['total_observations'] / data['count'],
                'series_density': data['count'] / sum(cat_data['count'] for cat_data in categories.values()),
                'observation_density': data['total_observations'] / sum(cat_data['total_observations'] for cat_data in categories.values())
            }
        
        # Find patterns
        highest_activity = max(category_stats.items(), key=lambda x: x[1]['avg_observations_per_series'])
        most_comprehensive = max(category_stats.items(), key=lambda x: x[1]['series_count'])
        
        # Calculate variation coefficients
        obs_per_series = [stats['avg_observations_per_series'] for stats in category_stats.values()]
        cv_observations = np.std(obs_per_series) / np.mean(obs_per_series)
        
        return {
            'category_statistics': category_stats,
            'key_insights': {
                'highest_activity_category': {
                    'category': highest_activity[0],
                    'avg_observations': highest_activity[1]['avg_observations_per_series']
                },
                'most_comprehensive_category': {
                    'category': most_comprehensive[0],
                    'series_count': most_comprehensive[1]['series_count']
                },
                'data_balance': {
                    'coefficient_of_variation': cv_observations,
                    'balance_quality': 'High' if cv_observations < 0.1 else 'Moderate' if cv_observations < 0.3 else 'Low'
                }
            }
        }
    
    def analyze_time_series_characteristics(self):
        """Analyze time series characteristics of household spending data"""
        print("Analyzing time series characteristics...")
        
        detailed_data = self.household_data['detailed_data']
        
        # Analyze time spans
        time_spans = []
        start_dates = []
        end_dates = []
        
        for series in detailed_data:
            if series['series_start'] and series['series_end']:
                start = pd.to_datetime(series['series_start'])
                end = pd.to_datetime(series['series_end'])
                span_years = (end - start).days / 365.25
                time_spans.append(span_years)
                start_dates.append(start)
                end_dates.append(end)
        
        if time_spans:
            # Calculate statistics
            mean_span = np.mean(time_spans)
            std_span = np.std(time_spans)
            earliest_start = min(start_dates)
            latest_end = max(end_dates)
            
            # Analyze observation frequency
            observations = [s['observations'] for s in detailed_data if s['observations']]
            if observations:
                avg_obs = np.mean(observations)
                median_obs = np.median(observations)
                
                # Calculate implied frequency
                avg_frequency = avg_obs / mean_span if mean_span > 0 else 0
        
        return {
            'temporal_characteristics': {
                'average_time_span_years': mean_span,
                'time_span_variability': std_span,
                'earliest_data_start': earliest_start.strftime('%Y-%m-%d'),
                'latest_data_end': latest_end.strftime('%Y-%m-%d'),
                'total_coverage_years': (latest_end - earliest_start).days / 365.25
            },
            'data_frequency_analysis': {
                'average_observations_per_series': avg_obs,
                'median_observations_per_series': median_obs,
                'implied_measurement_frequency': f"{avg_frequency:.1f} observations per year",
                'frequency_interpretation': 'Monthly' if 10 <= avg_frequency <= 14 else 'Quarterly' if 3 <= avg_frequency <= 5 else 'Annual' if avg_frequency <= 2 else 'High frequency'
            }
        }
    
    def analyze_data_completeness(self):
        """Analyze completeness and quality of the datasets"""
        print("Analyzing data completeness...")
        
        # Household spending completeness
        household_series = self.household_data['detailed_data']
        complete_series = sum(1 for s in household_series if all([
            s['series_id'], s['series_start'], s['series_end'], s['observations']
        ]))
        
        # Housing data completeness
        housing_tables = self.housing_data.get('available_tables', [])
        
        # Income data completeness
        income_tables = self.income_data.get('available_tables', [])
        
        completeness_score = {
            'household_spending': {
                'complete_series_ratio': complete_series / len(household_series),
                'data_richness': 'High - time series with metadata',
                'usability_score': 0.95
            },
            'housing_costs': {
                'available_tables': len(housing_tables),
                'data_richness': 'Medium - index only, requires additional sheets',
                'usability_score': 0.4
            },
            'income_work': {
                'available_tables': len(income_tables),
                'data_richness': 'Medium - index only, requires additional sheets',
                'usability_score': 0.4
            }
        }
        
        overall_score = np.mean([score['usability_score'] for score in completeness_score.values()])
        
        return {
            'dataset_completeness': completeness_score,
            'overall_usability_score': overall_score,
            'recommendations': [
                'Household spending data is ready for advanced analysis and visualization',
                'Housing and income datasets require access to individual table sheets',
                'Consider requesting full datasets from ABS for comprehensive analysis',
                'Current data sufficient for trend analysis and category comparisons'
            ]
        }
    
    def generate_correlation_opportunities(self):
        """Identify potential correlation and analysis opportunities"""
        print("Identifying correlation opportunities...")
        
        spending_categories = list(self.household_data['summary_statistics']['categories_breakdown'].keys())
        housing_tables = [t['description'] for t in self.housing_data.get('available_tables', [])]
        income_tables = [t['description'] for t in self.income_data.get('available_tables', [])]
        
        opportunities = {
            'direct_correlations': [
                {
                    'analysis_type': 'Spending vs Income Correlation',
                    'datasets': ['household_spending', 'income_work'],
                    'methodology': 'Compare discretionary spending patterns with personal/household income levels',
                    'expected_outcome': 'Identify income elasticity of different spending categories'
                },
                {
                    'analysis_type': 'Housing Affordability Impact',
                    'datasets': ['household_spending', 'housing_costs'],
                    'methodology': 'Analyze non-discretionary spending in relation to housing cost burden',
                    'expected_outcome': 'Understand how housing costs affect other household expenditure'
                }
            ],
            'temporal_analysis': [
                {
                    'analysis_type': 'COVID Impact Analysis',
                    'period': '2019-2021',
                    'methodology': 'Compare pre-COVID (2019) vs pandemic period spending patterns',
                    'focus_categories': ['Discretionary', 'Non Discretionary', 'Services', 'Goods']
                },
                {
                    'analysis_type': 'Recovery Pattern Analysis',
                    'period': '2021-2025',
                    'methodology': 'Analyze spending recovery patterns post-pandemic',
                    'focus_categories': spending_categories
                }
            ],
            'demographic_analysis': [
                {
                    'analysis_type': 'Age-based Spending Patterns',
                    'data_source': 'Income work tables with age breakdowns',
                    'correlation_target': 'Discretionary vs Non-discretionary spending ratios'
                },
                {
                    'analysis_type': 'Geographic Spending Variations',
                    'data_source': 'State/Territory breakdowns in income data',
                    'correlation_target': 'Regional spending pattern differences'
                }
            ]
        }
        
        return opportunities
    
    def generate_advanced_insights(self):
        """Generate comprehensive advanced insights"""
        print("Generating advanced insights...")
        
        spending_analysis = self.analyze_spending_patterns()
        time_series_analysis = self.analyze_time_series_characteristics()
        completeness_analysis = self.analyze_data_completeness()
        correlation_opportunities = self.generate_correlation_opportunities()
        
        insights = {
            'metadata': {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analysis_type': 'Advanced Statistical Analysis',
                'datasets_analyzed': ['household_spending', 'housing_costs', 'income_work']
            },
            'spending_pattern_analysis': spending_analysis,
            'time_series_analysis': time_series_analysis,
            'data_quality_analysis': completeness_analysis,
            'correlation_opportunities': correlation_opportunities,
            'strategic_recommendations': [
                'Focus visualization efforts on household spending data for immediate insights',
                'Develop time series dashboard showing monthly spending trends 2019-2025',
                'Create category comparison tools for discretionary vs non-discretionary analysis',
                'Build correlation matrix for spending categories',
                'Implement forecast models for spending trend projection',
                'Design interactive filters for temporal and category analysis'
            ]
        }
        
        return insights
    
    def save_analysis(self, analysis, filename):
        """Save analysis to JSON file"""
        filepath = os.path.join(self.processed_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"Saved {filename}")

def main():
    """Main execution function"""
    analyzer = AdvancedAnalyzer()
    
    # Generate comprehensive analysis
    insights = analyzer.generate_advanced_insights()
    
    # Save to file
    analyzer.save_analysis(insights, 'advanced_statistical_analysis.json')
    
    # Print summary
    print("\n" + "="*50)
    print("ADVANCED ANALYSIS COMPLETE")
    print("="*50)
    
    print(f"\nSpending Categories Analysis:")
    for category, stats in insights['spending_pattern_analysis']['category_statistics'].items():
        print(f"  • {category}: {stats['series_count']} series, {stats['total_observations']} observations")
    
    print(f"\nTime Series Characteristics:")
    temporal = insights['time_series_analysis']['temporal_characteristics']
    print(f"  • Average coverage: {temporal['average_time_span_years']:.1f} years")
    print(f"  • Data period: {temporal['earliest_data_start']} to {temporal['latest_data_end']}")
    
    frequency = insights['time_series_analysis']['data_frequency_analysis']
    print(f"  • Measurement frequency: {frequency['frequency_interpretation']}")
    
    print(f"\nData Usability Scores:")
    for dataset, score in insights['data_quality_analysis']['dataset_completeness'].items():
        print(f"  • {dataset}: {score['usability_score']:.2f} ({score['data_richness']})")
    
    print(f"\nReady for visualization and dashboard development!")

if __name__ == "__main__":
    main()
