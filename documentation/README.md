# Flu Vaccination Analysis Dashboard

A comprehensive analysis of flu vaccination trends across U.S. counties from 2009-2023, revealing significant disparities and opportunities for public health intervention.

## Overview

This project analyzes over 200,000 flu vaccination records across 1,944 counties to understand vaccination patterns, identify disparities, and provide actionable insights for healthcare providers and policymakers.

## Key Findings

### National Trends Show Concerning Decline
The data reveals a troubling pattern: while flu vaccination rates peaked around 2019-2021 (39%+ average), there's been a notable decline to 33.9% in 2023. This downward trend coincides with the COVID-19 pandemic, suggesting potential resource diversion or public health fatigue.

### Geographic Disparities Are Stark
County-level analysis uncovers dramatic differences in vaccination uptake:
- **Top performers**: Lower Connecticut River Valley (58.5%), Newport, RI (56.1%), Arlington, VA (55.0%)
- **Bottom performers**: Region 4, FL (18.0%), Starr, TX (20.1%), Nevada, CA (22.3%)

The 40+ percentage point gap between highest and lowest performing counties highlights significant inequities in healthcare access and public health infrastructure.

### Setting Matters More Than Expected
Where people get vaccinated reveals critical insights:
- **Medical settings**: Consistently highest rates (51-87% across age groups)
- **Workplace settings**: Alarmingly low (1-18% across all demographics)
- **Pharmacy/Store**: Moderate performance (7-40%)

This suggests that traditional workplace wellness programs are failing to reach employees effectively, while medical settings remain the most trusted vaccination venues.

### Age Disparities Persist
Children (6 months - 17 years) show the lowest overall rates at 29.1%, but interestingly, when they do get vaccinated, it's overwhelmingly in medical settings (86.7%). This indicates that pediatric vaccination relies heavily on healthcare provider recommendations rather than community-based programs.

### Racial and Ethnic Gaps Are Narrower Than Expected
While disparities exist, the range is relatively narrow:
- Asian, Non-Hispanic: 40.6%
- Black, Non-Hispanic: 33.3%

The 7.3 percentage point difference, while statistically significant, suggests that systemic barriers affect all groups, though some more than others.

## Data Sources

- **Primary Dataset**: 202,508 county-level flu vaccination records
- **Time Period**: 2009-2023 (15 years)
- **Geographic Coverage**: 1,944 counties across all 50 states
- **Demographic Dimensions**: Age groups, race/ethnicity, vaccination settings
- **Statistical Rigor**: 95% confidence intervals for all estimates

## Project Structure

```
├── data_cleaning.py                    # Data preprocessing and validation
├── data_aggregation.py                 # Multi-level data aggregation
├── multi_tab_dashboard.py              # Interactive Dash dashboard
├── Flu_shot_cleaned.csv               # Processed dataset (202K records)
├── aggregated_data/                    # Analysis-ready datasets
│   ├── county_agg.csv                 # County-level aggregations
│   ├── year_agg.csv                   # Yearly trend data
│   ├── dimension_agg.csv              # Demographic analysis
│   └── county_year_agg.csv            # County-year combinations
├── visualizations/                     # Interactive HTML charts
│   ├── county_choropleth_*.html       # Geographic maps
│   ├── county_trends_*.html           # Temporal trends
│   ├── dimension_*.html               # Demographic charts
│   └── national_trend.html            # National overview
└── documentation/                      # Analysis documentation
    ├── executive_summary.md           # Stakeholder summary
    ├── data_appendix.md               # Technical details
    └── project_summary.md             # Complete overview
```

## Getting Started

### Prerequisites
```bash
pip install pandas numpy plotly dash dash-bootstrap-components
```

### Running the Dashboard
```bash
python multi_tab_dashboard.py
```
Then open http://localhost:8050 in your browser.

### Exploring Individual Visualizations
Open any `.html` file in your browser to view specific analyses:
- `county_choropleth_main.html` - Main county map
- `county_trends_simplified.html` - Top vs bottom counties
- `dimension_overview.html` - Demographic summary

## Methodology

### Data Processing
1. **Cleaning**: Handled missing values, standardized formats, validated FIPS codes
2. **Aggregation**: Created county, year, and demographic-level summaries
3. **Validation**: Ensured statistical integrity with confidence intervals
4. **Geographic Mapping**: Integrated FIPS codes for accurate county mapping

### Statistical Approach
- **Confidence Intervals**: 95% CI for all vaccination rate estimates
- **Outlier Detection**: Identified counties with extreme rates or wide CIs
- **Trend Analysis**: Multi-year patterns with policy event markers
- **Disparity Measurement**: Quantified gaps across demographic groups

## Insights for Public Health

### Immediate Actions Needed
1. **Target Low-Performing Counties**: Focus resources on bottom 20% (rates <30%)
2. **Address Workplace Gaps**: Implement effective workplace vaccination programs
3. **Pediatric Outreach**: Develop community-based programs for children
4. **Rural Access**: Deploy mobile vaccination services to underserved areas

### Policy Recommendations
1. **Geographic Equity**: Ensure all counties achieve minimum 30% coverage
2. **Setting Diversification**: Expand beyond medical settings to pharmacies and workplaces
3. **Demographic Targeting**: Develop culturally appropriate outreach programs
4. **Data Infrastructure**: Implement real-time monitoring systems

## Technical Details

### Data Quality
- **Completeness**: 91.7% data retention after cleaning
- **Accuracy**: FIPS code validation against US Census data
- **Consistency**: Multi-year trend validation
- **Reliability**: Confidence intervals for uncertainty quantification

### Visualization Features
- **Interactive Charts**: Hover details, filtering, export capabilities
- **Geographic Mapping**: FIPS-based choropleth maps with state/county selection
- **Statistical Rigor**: Error bars, confidence intervals, outlier highlighting
- **Responsive Design**: Works across devices and screen sizes

## Future Enhancements

- **Real-time Data Integration**: Automated data refresh capabilities
- **Predictive Modeling**: Forecasting vaccination trends
- **Advanced Analytics**: Machine learning for pattern recognition
- **Mobile Optimization**: Enhanced mobile dashboard experience

## Contributing

This analysis provides a foundation for ongoing flu vaccination monitoring and improvement. The codebase is designed for extensibility and can be adapted for other vaccination types or geographic regions.

## License

This project is open source and available for public health research and policy development.

---

*This analysis represents a comprehensive approach to public health data science, transforming raw vaccination data into actionable insights that can improve health outcomes for millions of Americans.*
