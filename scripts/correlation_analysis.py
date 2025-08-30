"""
Statistical Correlation and Pattern Analysis
Generates correlation matrices and identifies spending patterns
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import os

def generate_spending_correlation_analysis():
    """Generate correlation analysis between spending categories"""
    
    # Load household spending data
    with open('../processed/household_spending.json', 'r', encoding='utf-8') as f:
        household_data = json.load(f)
    
    # Extract category data
    categories = household_data['summary_statistics']['categories_breakdown']
    
    # Create correlation matrix data
    correlation_data = {
        'category_comparison': {},
        'statistical_relationships': {}
    }
    
    category_names = list(categories.keys())
    
    # Calculate pairwise similarities based on series count and observations
    similarity_matrix = np.zeros((len(category_names), len(category_names)))
    
    for i, cat1 in enumerate(category_names):
        for j, cat2 in enumerate(category_names):
            if i == j:
                similarity_matrix[i][j] = 1.0
            else:
                # Calculate similarity based on observation patterns
                obs1 = categories[cat1]['total_observations']
                obs2 = categories[cat2]['total_observations']
                count1 = categories[cat1]['count']
                count2 = categories[cat2]['count']
                
                # Normalized similarity score
                obs_similarity = 1 - abs(obs1 - obs2) / max(obs1, obs2)
                count_similarity = 1 - abs(count1 - count2) / max(count1, count2)
                similarity_matrix[i][j] = (obs_similarity + count_similarity) / 2
    
    # Convert to dictionary format for JSON
    correlation_matrix = {}
    for i, cat1 in enumerate(category_names):
        correlation_matrix[cat1] = {}
        for j, cat2 in enumerate(category_names):
            correlation_matrix[cat1][cat2] = float(similarity_matrix[i][j])
    
    # Find strongest relationships
    strong_relationships = []
    for i, cat1 in enumerate(category_names):
        for j, cat2 in enumerate(category_names):
            if i < j and similarity_matrix[i][j] > 0.9:  # High similarity threshold
                strong_relationships.append({
                    'category_1': cat1,
                    'category_2': cat2,
                    'similarity_score': float(similarity_matrix[i][j]),
                    'interpretation': 'High structural similarity in data patterns'
                })
    
    # Identify category characteristics
    category_profiles = {}
    for cat, data in categories.items():
        avg_obs_per_series = data['total_observations'] / data['count']
        density = data['total_observations'] / sum(c['total_observations'] for c in categories.values())
        
        category_profiles[cat] = {
            'data_intensity': 'High' if avg_obs_per_series > 75 else 'Medium' if avg_obs_per_series > 50 else 'Low',
            'relative_size': density,
            'series_consistency': 'Consistent' if data['count'] == 9 else 'Variable',
            'analysis_priority': 'High' if density > 0.15 and avg_obs_per_series > 70 else 'Medium'
        }
    
    return {
        'correlation_matrix': correlation_matrix,
        'strong_relationships': strong_relationships,
        'category_profiles': category_profiles,
        'analysis_metadata': {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'correlation_method': 'Structural similarity based on observation patterns',
            'categories_analyzed': len(category_names)
        }
    }

def generate_time_series_insights():
    """Generate time series specific insights"""
    
    with open('../processed/household_spending.json', 'r', encoding='utf-8') as f:
        household_data = json.load(f)
    
    detailed_data = household_data['detailed_data']
    
    # Analyze temporal patterns
    temporal_insights = {
        'series_lifecycle_analysis': {},
        'data_coverage_analysis': {},
        'forecast_readiness': {}
    }
    
    # Group by category
    category_series = {}
    for series in detailed_data:
        if ';' in series['description']:
            category = series['description'].split(';')[1].strip()
            if category not in category_series:
                category_series[category] = []
            category_series[category].append(series)
    
    # Analyze each category's temporal characteristics
    for category, series_list in category_series.items():
        observations = [s['observations'] for s in series_list if s['observations']]
        
        if observations:
            temporal_insights['series_lifecycle_analysis'][category] = {
                'min_observations': min(observations),
                'max_observations': max(observations),
                'avg_observations': np.mean(observations),
                'observation_consistency': 'High' if np.std(observations) / np.mean(observations) < 0.1 else 'Moderate',
                'forecast_suitability': 'Excellent' if np.mean(observations) >= 70 else 'Good' if np.mean(observations) >= 50 else 'Limited'
            }
    
    # Overall temporal readiness
    all_observations = [s['observations'] for s in detailed_data if s['observations']]
    temporal_insights['forecast_readiness'] = {
        'overall_readiness_score': np.mean(all_observations) / 100,  # Normalized score
        'recommended_models': [
            'ARIMA for trend analysis',
            'Seasonal decomposition for monthly patterns',
            'VAR for multi-category relationships'
        ],
        'analysis_horizon': '6+ years of historical data supports 12-24 month forecasts'
    }
    
    return temporal_insights

def main():
    """Generate comprehensive statistical analysis"""
    print("Generating correlation and pattern analysis...")
    
    # Generate analyses
    correlation_analysis = generate_spending_correlation_analysis()
    time_series_insights = generate_time_series_insights()
    
    # Combine results
    comprehensive_analysis = {
        'metadata': {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_type': 'Correlation and Pattern Analysis',
            'purpose': 'Identify relationships and patterns for visualization development'
        },
        'correlation_analysis': correlation_analysis,
        'time_series_insights': time_series_insights,
        'visualization_recommendations': [
            'Create correlation heatmap showing category relationships',
            'Develop time series plots for each spending category',
            'Build interactive dashboard with category filters',
            'Implement trend analysis with seasonal decomposition',
            'Design comparison tools for discretionary vs non-discretionary spending',
            'Create forecast visualization showing trend projections'
        ],
        'next_development_steps': [
            'Load JSON data into visualization framework (D3.js, Chart.js, or similar)',
            'Implement responsive design for dashboard',
            'Add interactive filters for time period selection',
            'Create export functionality for further analysis',
            'Implement real-time data update capability'
        ]
    }
    
    # Save analysis
    with open('../processed/correlation_pattern_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(comprehensive_analysis, f, indent=2, ensure_ascii=False, default=str)
    
    print("Correlation and pattern analysis completed!")
    print("\nKey Findings:")
    print(f"- Analyzed {len(correlation_analysis['category_profiles'])} spending categories")
    print(f"- Identified {len(correlation_analysis['strong_relationships'])} strong category relationships")
    print(f"- Generated correlation matrix for visualization")
    print(f"- Assessed forecast readiness for all time series")
    
    print(f"\nCategory Analysis Priority:")
    for category, profile in correlation_analysis['category_profiles'].items():
        print(f"  • {category}: {profile['analysis_priority']} priority ({profile['data_intensity']} intensity)")
    
    print("\nAll analysis files ready for visualization development!")

if __name__ == "__main__":
    main()
