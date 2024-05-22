import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from plotly import express as px
from plotly import graph_objects as go
import string
import dash
from dash import dcc, html

start_time = datetime.datetime.now()

initial_data = pd.read_excel('/Users/tinashem/Github Repos/CareerPalz/files/LCA_Disclosure_Data_FY2023_final_copy.xlsx')

data = initial_data.copy()

end_time = datetime.datetime.now()

print('Duration: {}'.format(end_time - start_time))

new_employment = data[(data['NEW_EMPLOYMENT'] != 0) & (data['FULL_TIME_POSITION'] == 'Y')]
certified = new_employment[new_employment['CASE_STATUS'] == 'Certified']
certified_h1b = certified[certified['VISA_CLASS'] == 'H-1B']

# Let's use a new file downloaded from the DOL website to cross-validate the data entered in the SOC_TITLE column
soc_definitions = pd.read_excel('/Users/tinashem/Downloads/soc_2018_definitions_detailed_occupations.xlsx')

# let's narrow down the soc_definitions data frame to only the entries categorized as "Detailed" for the SOC_GROUP
soc_definitions_detailed = soc_definitions[soc_definitions['SOC_GROUP'] == 'Detailed']

# let's check for data types
for col in soc_definitions_detailed.columns:
    print(f"{col}: {soc_definitions_detailed[col].values[0]}: {type(soc_definitions_detailed[col].values[0])}")

# Now that we know that the data types match, let's cross-validate the entries in the SOC_TITLE column of the certified_h1b data frame with the SOC_TITLE column of the soc_definitions_detailed data frame

# let's start by printing out the number of SOC titles in the certified_h1b data frame
print(f"There are {certified_h1b['SOC_TITLE'].nunique():,} unique SOC titles in the certified_h1b data frame.")

# let's print out the number of SOC titles in the soc_definitions_detailed data frame
print(f"There are {soc_definitions_detailed['SOC_TITLE'].nunique():,} unique SOC titles in the soc_definitions_detailed data frame.")
# This is less than the 867 unique SOC titles in the soc_definitions_detailed data frame, so let's cross-validate the two data frames
certified_h1b_soc_titles = certified_h1b['SOC_TITLE'].unique()
soc_definitions_detailed_soc_titles = soc_definitions_detailed['SOC_TITLE'].unique()

# let's find the SOC titles that are in the certified_h1b data frame but not in the soc_definitions_detailed data frame
missing_from_certified_h1b = [title for title in certified_h1b_soc_titles if title not in soc_definitions_detailed_soc_titles]
print(f"There are {len(missing_from_certified_h1b):,} SOC titles in the certified_h1b data frame that are not in the soc_definitions_detailed data frame.")

# let's find the SOC titles that are in the soc_definitions_detailed data frame but not in the certified_h1b data frame
missing_from_soc_definitions = [title for title in soc_definitions_detailed_soc_titles if title not in certified_h1b_soc_titles]
print(f"There are {len(missing_from_soc_definitions):,} SOC titles in the soc_definitions_detailed data frame that are not in the certified_h1b data frame.")

# let's find the SOC titles that are in both the certified_h1b data frame and the soc_definitions_detailed data frame
common_soc_titles = [title for title in certified_h1b_soc_titles if title in soc_definitions_detailed_soc_titles]
print(f"There are {len(common_soc_titles):,} SOC titles that are in both the certified_h1b data frame and the soc_definitions_detailed data frame.")
print(f"The first 10 SOC titles that are in the certified_h1b df that are not in the soc_definitions_detailed df are {missing_from_certified_h1b[:10]}")

# missing_from_certified_h1b[0] in soc_definitions_detailed_soc_titles
# After looking through some of the entries in the two dataframes being investigated, it appears that some entries in the certified_h1b dataframe are not in the soc_definitions_detailed dataframe, likely due to incorrect entry. For example, "Software Quality Assurance Analysts and Testers" is incorrectly entered as "Software Quality Assurance Engineers and Testers". Another example, "Business Intelligence Analysts" and "Bioinformatics Scientists" are not in the SOC Definitions.
# I have decided to remove these entries from the certified_h1b dataframe.

# let's drop the rows in the certified_h1b data frame that have SOC titles that are not in the soc_definitions_detailed data frame
certified_h1b_renewed = certified_h1b.copy()
certified_h1b_renewed = certified_h1b_renewed[certified_h1b_renewed['SOC_TITLE'].isin(common_soc_titles)]
print(f"There are {certified_h1b_renewed['SOC_TITLE'].nunique():,} unique SOC titles in the certified_h1b_renewed data frame.")

# let's re-do the Dash app
# Let's display the Plotly graph from before in a Dash app with a dropdown menu that selects the different SOC titles
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='soc-title-dropdown',
        options=[{'label': title, 'value': title} for title in certified_h1b_renewed['SOC_TITLE'].unique()],
        value='Certified LCAs'
    ),
    dcc.Graph(
        id='soc-title-bar-graph'
    ),
    dcc.Dropdown(
        id='employer-dropdown',
        options=[{'label': title, 'value': title} for title in certified_h1b_renewed['JOB_TITLE'].unique()],
        value='Certified LCAs for Employers'
    ),
    dcc.Graph(
        id='employer-bar-graph'
    )
])

@app.callback(
    dash.dependencies.Output('soc-title-bar-graph', 'figure'),
    [dash.dependencies.Input('soc-title-dropdown', 'value')]
)
def update_bar_graph(selected_soc_title):
    filtered_data = certified_h1b_renewed[certified_h1b_renewed['SOC_TITLE'] == selected_soc_title]
    fig = go.Figure(go.Bar(
        x=filtered_data['JOB_TITLE'].value_counts()[0:20].values,
        y=filtered_data['JOB_TITLE'].value_counts()[0:20].index,
        orientation='h',
        marker_color='green',
        text=filtered_data['JOB_TITLE'].value_counts().values,
        textposition='outside')
    )
    fig.update_layout(
        title=f'Top 20 Job Titles for \"{selected_soc_title}\" out of {filtered_data["JOB_TITLE"].nunique():,} different entries',
        xaxis=dict(title=f'Number of Certified LCA\'s out of {filtered_data.shape[0]:,} total certified LCA\'s'),
        yaxis=dict(
            categoryorder='total ascending',
            tickangle=0,
            ticklabelstep=1,
            title='Job Title'),
        titlefont={'family': 'Times New Roman'}
    )
    fig.layout.yaxis.tickfont.size = 6 # type: ignore
    fig.layout.hoverlabel.font.family = 'Times New Roman' # type: ignore
    return fig

@app.callback(
    dash.dependencies.Output('employer-bar-graph', 'figure'),
    [dash.dependencies.Input('employer-dropdown', 'value')]
)
def update_bar_graph_employer(selected_job_title):
    filtered_data = certified_h1b_renewed[certified_h1b_renewed['JOB_TITLE'] == selected_job_title]
    fig = go.Figure(go.Bar(
        x=filtered_data['EMPLOYER_NAME'].value_counts()[0:20].values,
        y=filtered_data['EMPLOYER_NAME'].value_counts()[0:20].index,
        orientation='h',
        marker_color='purple',
        text=filtered_data['EMPLOYER_NAME'].value_counts().values,
        textposition='outside')
    )
    fig.update_layout(
        title =f'Up to Top 20 Employers for Job Title selected as {selected_job_title} out of {filtered_data["EMPLOYER_NAME"].nunique():,} different employers',
        xaxis=dict(title=f'Number of Certified LCA\'s out of {filtered_data.shape[0]:,} total certified LCA\'s'),
        yaxis=dict(
            categoryorder='total ascending',
            tickangle=0,
            ticklabelstep=1,
            title='Employers'),
        titlefont={'family': 'Times New Roman'}
    )
    fig.layout.yaxis.tickfont.size = 6 # type: ignore
    fig.layout.hoverlabel.font.family = 'Times New Roman' # type: ignore
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)