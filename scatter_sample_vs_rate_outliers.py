import pandas as pd
import numpy as np
import plotly.graph_objects as go

INPUT_FILE = 'Flu_shot_cleaned.csv'
OUTPUT_FILE = 'sample_vs_rate_outliers.html'

# Configuration
MOST_RECENT_ONLY = True  # set to False to include all years
RATE_OUTLIER_QUANTILE = 0.025  # bottom/top 2.5%
CI_WIDTH_OUTLIER_QUANTILE = 0.975  # top 2.5% widest CI
TOP_LABELS = 5


def aggregate_county_year(df: pd.DataFrame) -> pd.DataFrame:
	grp = df.groupby(['Geography', 'FIPS', 'Season/Survey Year'], as_index=False).agg(
		avg_rate=('Estimate (%)', 'mean'),
		avg_ci_lower=('ci_lower', 'mean'),
		avg_ci_upper=('ci_upper', 'mean'),
		record_count=('Estimate (%)', 'count'),
		sample_size_nonnull=('Sample Size', lambda s: s.dropna().sum())
	)
	grp['sample_size'] = grp['sample_size_nonnull'].replace(0, np.nan)
	grp['sample_size'] = grp['sample_size'].fillna(grp['record_count'])
	grp.drop(columns=['sample_size_nonnull'], inplace=True)
	grp['ci_width'] = grp['avg_ci_upper'] - grp['avg_ci_lower']
	return grp


def detect_outliers(ds: pd.DataFrame) -> pd.DataFrame:
	# Determine thresholds based on quantiles
	low_thr = ds['avg_rate'].quantile(RATE_OUTLIER_QUANTILE)
	high_thr = ds['avg_rate'].quantile(1 - RATE_OUTLIER_QUANTILE)
	ci_thr = ds['ci_width'].quantile(CI_WIDTH_OUTLIER_QUANTILE)

	is_low = ds['avg_rate'] <= low_thr
	is_high = ds['avg_rate'] >= high_thr
	is_wide = ds['ci_width'] >= ci_thr
	outlier = is_low | is_high | is_wide

	# Score outliers: distance from nearest threshold (normalized)
	rate_center = np.where(is_low, low_thr - ds['avg_rate'], np.where(is_high, ds['avg_rate'] - high_thr, 0))
	rate_score = (rate_center - rate_center.min()) / (rate_center.max() - rate_center.min() + 1e-9)
	ci_score = np.where(is_wide, ds['ci_width'] - ci_thr, 0)
	ci_score = (ci_score - np.min(ci_score)) / (np.max(ci_score) - np.min(ci_score) + 1e-9)
	outlier_score = rate_score + ci_score

	res = ds.copy()
	res['is_outlier'] = outlier
	res['outlier_score'] = outlier_score
	return res, low_thr, high_thr, ci_thr


def build_plot(ds: pd.DataFrame, year_label: str):
	colors = np.where(ds['is_outlier'], 'crimson', 'rgba(31,119,180,0.5)')
	sizes = np.clip((ds['record_count'] / ds['record_count'].max()) * 14 + 4, 6, 18)

	fig = go.Figure()
	fig.add_trace(go.Scatter(
		x=ds['sample_size'], y=ds['avg_rate'],
		mode='markers',
		marker=dict(color=colors, size=sizes, line=dict(color='white', width=0.5)),
		text=ds['Geography'],
		customdata=np.column_stack((ds['Season/Survey Year'], ds['avg_ci_lower'], ds['avg_ci_upper'], ds['ci_width'], ds['record_count'])),
		hovertemplate='<b>%{text}</b><br>' +
			'Year: %{customdata[0]}<br>' +
			'Sample Size: %{x:.0f}<br>' +
			'Vaccination Rate: %{y:.1f}%<br>' +
			'95% CI: %{customdata[1]:.1f}–%{customdata[2]:.1f}% (width %{customdata[3]:.1f})<br>' +
			'Records: %{customdata[4]}<extra></extra>'
	))

	# Label top outliers
	labels = ds.sort_values('outlier_score', ascending=False).head(TOP_LABELS)
	for _, row in labels.iterrows():
		fig.add_annotation(
			x=row['sample_size'], y=row['avg_rate'], text=row['Geography'],
			showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1,
			arrowcolor='black', bgcolor='rgba(255,255,255,0.9)',
			ax=20, ay=-20, font=dict(size=10)
		)

	fig.update_layout(
		title={'text': f'Sample Size vs Flu Vaccination Rate ({year_label})<br><sub>Outliers highlighted: extreme rates or wide confidence intervals</sub>', 'x': 0.5},
		xaxis_title='Sample Size (proxy; records if missing)',
		yaxis_title='Vaccination Rate (%)',
		width=1100, height=700,
		margin=dict(l=70, r=20, t=90, b=70)
	)
	fig.update_yaxes(range=[0, 100])
	fig.write_html(OUTPUT_FILE)
	print(f'Saved: {OUTPUT_FILE}')


def main():
	print('Loading cleaned dataset...')
	df = pd.read_csv(INPUT_FILE)
	agg = aggregate_county_year(df)

	if MOST_RECENT_ONLY:
		year = int(agg['Season/Survey Year'].max())
		print(f'Using most recent year: {year}')
		agg = agg[agg['Season/Survey Year'] == year].copy()
		year_label = str(year)
	else:
		year_label = 'All Years'

	res, low_thr, high_thr, ci_thr = detect_outliers(agg)
	print(f'Outlier thresholds -> Low rate ≤ {low_thr:.1f}%, High rate ≥ {high_thr:.1f}%, CI width ≥ {ci_thr:.1f}')
	build_plot(res, year_label)

if __name__ == '__main__':
	main()
