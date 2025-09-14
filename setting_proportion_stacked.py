import pandas as pd
import numpy as np
import plotly.graph_objects as go

INPUT_FILE = 'Flu_shot_cleaned.csv'
OUTPUT_FILE = 'setting_proportions_stacked.html'

SETTING_NAMES = ['Medical Setting', 'Non-Medical Setting', 'Pharmacy/Store', 'Workplace', 'School']


def build_setting_proportions():
	print('Loading cleaned dataset...')
	df = pd.read_csv(INPUT_FILE)

	# Filter to rows that map to settings across all dimension types where available
	mask = df['Dimension'].isin(SETTING_NAMES)
	ds = df.loc[mask, ['Season/Survey Year', 'Dimension', 'Estimate (%)']].copy()
	if ds.empty:
		raise ValueError('No rows found for requested settings in the cleaned dataset.')

	# Aggregate: average coverage by year and setting
	agg = ds.groupby(['Season/Survey Year', 'Dimension'], as_index=False)['Estimate (%)'].mean()
	agg.rename(columns={'Estimate (%)': 'avg_rate'}, inplace=True)

	# Pivot to wide with settings as columns
	wide = agg.pivot(index='Season/Survey Year', columns='Dimension', values='avg_rate').reindex(columns=SETTING_NAMES)

	# Normalize each year to proportions that sum to 100%
	row_sum = wide.sum(axis=1)
	proportions = (wide.div(row_sum, axis=0) * 100).fillna(0)
	proportions = proportions.reset_index().sort_values('Season/Survey Year')

	years = proportions['Season/Survey Year'].tolist()

	fig = go.Figure()
	colors = {
		'Medical Setting': '#1f77b4',
		'Non-Medical Setting': '#2ca02c',
		'Pharmacy/Store': '#ff7f0e',
		'Workplace': '#d62728',
		'School': '#9467bd'
	}

	for setting in SETTING_NAMES:
		if setting in proportions.columns:
			fig.add_trace(go.Bar(
				x=years,
				y=proportions[setting].values,
				name=setting,
				marker_color=colors.get(setting, None),
				hovertemplate=f'<b>{setting}</b><br>Year: %{{x}}<br>Share: %{{y:.1f}}%<extra></extra>'
			))

	fig.update_layout(
		barmode='stack',
		yaxis=dict(title='Proportion of Settings (%)', range=[0, 100]),
		xaxis=dict(title='Year', dtick=1),
		title={
			'text': 'Proportion of Vaccinations by Setting Over Time (Normalized per Year)<br><sub>Shares computed from average reported rates across settings each year</sub>',
			'x': 0.5, 'xanchor': 'center'
		},
		legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
		width=1200, height=650,
		margin=dict(l=60, r=20, t=100, b=100)
	)

	fig.write_html(OUTPUT_FILE)
	print(f'Saved: {OUTPUT_FILE}')

if __name__ == '__main__':
	build_setting_proportions()
