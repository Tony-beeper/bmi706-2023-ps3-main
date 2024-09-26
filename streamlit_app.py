import altair as alt
import pandas as pd
import streamlit as st

@st.cache
def load_data():
    # Load and clean cancer data
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt(
        id_vars=["Country", "Year", "Cancer", "Sex"],
        var_name="Age",
        value_name="Deaths",
    )

    # Load and clean population data
    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(
        id_vars=["Country", "Year", "Sex"],
        var_name="Age",
        value_name="Pop",
    )

    # Merge cancer and population data
    df = pd.merge(left=cancer_df, right=pop_df, how="left")
    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")
    df.dropna(inplace=True)

    # Group and calculate rates
    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000

    return df

# Uncomment the next line when finished
df = load_data()

st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# Add a slider to select the year
year = st.slider(
    "Select Year",
    min_value=int(df["Year"].min()), 
    max_value=int(df["Year"].max()), 
    value=int(df["Year"].min()),  # default value, can be adjusted
    step=1
)

# Subset the dataframe based on the selected year
subset = df[df["Year"] == year]
### P2.1 ###

st.write(subset)


import streamlit as st

### P2.2 ###
# Add a radio button to select sex
sex = st.radio(
    "Select Sex",
    options=["M", "F"],  # Assuming "M" and "F" are the only options in the dataset
    index=0  # Default to "M"
)

# Filter the subset DataFrame based on the selected sex
subset = subset[subset["Sex"] == sex]
### P2.2 ###

st.write(subset)


### P2.3 ###
# Get a list of unique countries from the dataset
all_countries = df["Country"].unique().tolist()

# Add a multiselect widget to select countries
countries = st.multiselect(
    "Select Countries",
    options=all_countries,
    default=[
        "Austria",
        "Germany",
        "Iceland",
        "Spain",
        "Sweden",
        "Thailand",
        "Turkey",
    ]  # These are the default countries pre-selected
)

# Filter the subset DataFrame based on selected countries
subset = subset[subset["Country"].isin(countries)]
### P2.3 ###

st.write(subset)


### P2.4 ###
# Get the unique cancer types from the dataset
cancer_types = subset["Cancer"].unique().tolist()

# Add a dropdown select box for cancer type
cancer = st.selectbox(
    "Select Cancer Type",
    options=cancer_types,
    index=cancer_types.index("Malignant neoplasm of stomach")  # Default value
)

# Filter the subset DataFrame based on the selected cancer type
subset = subset[subset["Cancer"] == cancer]
### P2.4 ###

st.write(subset)

### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

# Create a selection brush to be used for selecting age groups
brush = alt.selection_interval(encodings=['x'])

# Create a heatmap comparing the cancer mortality rates
chart = alt.Chart(subset).mark_rect().encode(
    x=alt.X("Age", sort=ages, title="Age Group"),
    y=alt.Y("Country", title="Country"),
    color=alt.Color(
        "Rate",
        scale=alt.Scale(type="log", domain=[0.01, 1000], clamp=True),
        title="Mortality rate per 100k",
    ),
    tooltip=["Country", "Age", "Rate"],
).add_params(
    brush
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
)

# Create a bar chart that responds to the brush selection
chart2 = alt.Chart(subset).mark_bar().encode(
    x=alt.X("Age", sort=ages),
    y=alt.Y("Rate", title="Mortality rate per 100k"),
    color="Country",
    tooltip=["Rate"],
).transform_filter(
    brush
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
)

### P2.5 ###

# Display the heatmap and bar chart side by side
st.altair_chart(chart & chart2, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data available for the given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
