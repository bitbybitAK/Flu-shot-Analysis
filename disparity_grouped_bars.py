import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import List, Dict

INPUT_FILE = 'Flu_shot_cleaned.csv'

OUTPUTS = {
	'Age': 'disparities_age_grouped.html',
	'Race and Ethnicity': 'disparities_race_grouped.html',
	'Setting': 'disparities_setting_grouped.html'
}

SETTING_NAMES = ['Medical Setting', 'Non-Medical Setting', 'Pharmacy/Store', 'Workplace', 'School']


def aggregate_by_year_and_dimension(df: pd.DataFrame, dim_type: str) -> pd.DataFrame:
	if dim_type == 'Setting':
		mask = df['Dimension'].isin(SETTING_NAMES)
		df_sub = df.loc[mask].copy()
		group_cols = ['Season/Survey Year', 'Dimension']
	else:
		df_sub = df[df['Dimension Type'] == dim_type].copy()
		group_cols = ['Season/Survey Year', 'Dimension']

	agg = df_sub.groupby(group_cols).agg(
		avg_rate=('Estimate (%)','mean'),
		avg_lower=('ci_lower','mean'),
		avg_upper=('ci_upper','mean'),
		records=('Estimate (%)','count')
	).reset_index()
	return agg.sort_values(['Season/Survey Year','Dimension'])


def compute_yearly_gaps(agg: pd.DataFrame) -> pd.DataFrame:
	# For each year, compute highest and lowest subgroup and the gap
	def per_year(g: pd.DataFrame) -> pd.Series:
		idx_max = g['avg_rate'].idxmax()
		idx_min = g['avg_rate'].idxmin()
		return pd.Series({
			'max_dimension': g.loc[idx_max, 'Dimension'],
			'max_rate': g.loc[idx_max, 'avg_rate'],
			'min_dimension': g.loc[idx_min, 'Dimension'],
			'min_rate': g.loc[idx_min, 'avg_rate'],
			'gap': g.loc[idx_max, 'avg_rate'] - g.loc[idx_min, 'avg_rate']
		})
	gaps = agg.groupby('Season/Survey Year').apply(per_year).reset_index()
	return gaps


def build_grouped_bar(agg: pd.DataFrame, gaps: pd.DataFrame, dim_type: str, output_file: str, national_yearly: pd.DataFrame):
	# Pivot to ensure consistent subgroup ordering
	subgroups: List[str] = sorted(agg['Dimension'].unique().tolist())
	years: List[int] = sorted(agg['Season/Survey Year'].unique().tolist())

	fig = go.Figure()

	# Merge to get for each (year, subgroup) values
	# Build traces per subgroup (grouped bars by x=year)
	for subgroup in subgroups:
		ds = agg[agg['Dimension'] == subgroup].set_index('Season/Survey Year').reindex(years)
		y = ds['avg_rate'].values
		ci_upper = ds['avg_upper'].values
		ci_lower = ds['avg_lower'].values
		err_plus = (ci_upper - y)
		err_minus = (y - ci_lower)

		# Determine which years this subgroup is max or min to highlight borders
		is_max = gaps.set_index('Season/Survey Year').reindex(years)['max_dimension'].eq(subgroup).fillna(False).values
		is_min = gaps.set_index('Season/Survey Year').reindex(years)['min_dimension'].eq(subgroup).fillna(False).values
		line_width = [3 if (mx or mn) else 1 for mx, mn in zip(is_max, is_min)]
		line_color = ['green' if mx else ('crimson' if mn else 'black') for mx, mn in zip(is_max, is_min)]

		fig.add_trace(go.Bar(
			x=years, y=y, name=subgroup,
			error_y=dict(type='data', array=err_plus, arrayminus=err_minus, visible=True, thickness=1.5, color='black'),
			marker=dict(line=dict(width=line_width, color=line_color)),
			hovertemplate=f'<b>{subgroup}</b><br>Year: %{{x}}<br>Rate: %{{y:.1f}}%<br>CI: %{{customdata[0]:.1f}} - %{{customdata[1]:.1f}}%<extra></extra>',
			customdata=np.column_stack((ci_lower, ci_upper))
		))

	# Add national average line as a reference (same across subplots)
	nat = national_yearly.sort_values('Season/Survey Year')
	fig.add_trace(go.Scatter(
		x=nat['Season/Survey Year'], y=nat['national_avg'],
		mode='lines', name='National Avg', line=dict(color='gray', width=2, dash='dash'),
		yaxis='y', hovertemplate='Year: %{x}<br>National: %{y:.1f}%<extra></extra>'
	))

	# Add gap annotations per year at top
	for _, row in gaps.iterrows():
		year = int(row['Season/Survey Year'])
		gap_val = float(row['gap'])
		fig.add_annotation(
			x=year, y=max(agg[agg['Season/Survey Year']==year]['avg_upper'].max(), nat[nat['Season/Survey Year']==year]['national_avg'].iloc[0]) + 2,
			text=f"Gap: {gap_val:.1f} pp",
			showarrow=False, font=dict(size=10), bgcolor='rgba(255,255,255,0.8)'
		)

	fig.update_layout(
		barmode='group',
		title={
			'text': f'{dim_type}: Vaccination Rates by Subgroup Across Years<br><sub>Bars = subgroups with 95% CI; border highlight: green = highest, red = lowest per year; dashed line = national average</sub>',
			'x': 0.5, 'xanchor': 'center'
		},
		xaxis_title='Year', yaxis_title='Vaccination Rate (%)',
		width=1400, height=700,
		legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
		margin=dict(l=60, r=20, t=100, b=100)
	)
	fig.update_xaxes(dtick=1)
	fig.update_yaxes(range=[0, 100])

	fig.write_html(output_file)
	print(f'Saved: {output_file}')


def main():
	print('Loading cleaned dataset...')
	df = pd.read_csv(INPUT_FILE)

	# Compute national average by year
	national_yearly = df.groupby('Season/Survey Year', as_index=False)['Estimate (%)'].mean()
	national_yearly.rename(columns={'Estimate (%)': 'national_avg'}, inplace=True)

	for dim_type, out in OUTPUTS.items():
		print(f"\nProcessing: {dim_type}")
		agg = aggregate_by_year_and_dimension(df, dim_type)
		gaps = compute_yearly_gaps(agg)
		build_grouped_bar(agg, gaps, dim_type, out, national_yearly)

	print('\nAll charts saved.')

if __name__ == '__main__':
	main()
