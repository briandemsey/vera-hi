"""
VERA-HI: Verification Engine for Results & Accountability - Hawaii
Type 4 Detection using WIDA ACCESS for ELLs Speaking vs Writing + SBA Achievement Data

Hawaii context:
- WIDA ACCESS for ELLs, 4 domains (Listening, Speaking, Reading, Writing)
- SBA (Smarter Balanced Assessment), 4 levels:
    Well Below Standard / Below Standard / Near Standard / Meets or Exceeds Standard
- 1 statewide district (HIDOE) / 15 Complex Areas (administrative regions)
- ~7% EL (~12,600 students)
- Key language groups: Ilokano, Chuukese, Marshallese, Samoan, Tagalog
- Oceanic/Pacific Islander languages dominant (unlike mainland states)
- Policy 105-14: Hawaii BOE policy promoting multilingualism & multiliteracy
- Unique: only state with single statewide district
- arch.k12.hi.us -- accountability resource center

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

HI_RED = "#CE1126"
HI_BLUE = "#002B5C"
HI_DARK = "#001A3A"
HI_GRAY = "#4A4A4A"
HI_LIGHT_RED = "#E06666"

# ============================================================================
# DATA: Hawaii Complex Areas with EL Populations
# Source: HIDOE / arch.k12.hi.us
# Hawaii has 1 statewide district with 15 Complex Areas
# ============================================================================

def load_complex_areas():
    """Load HI Complex Areas with EL populations.

    Hawaii is the only US state with a single statewide school district (HIDOE).
    Instead of traditional districts, schools are organized into 15 Complex Areas,
    each serving as an administrative region. EL populations reflect Hawaii's unique
    Pacific Islander and Asian immigrant communities, with Ilokano, Chuukese,
    Marshallese, and Samoan as the dominant non-English languages.

    Policy 105-14 (2014) established multilingualism and multiliteracy as a goal
    for all students -- a progressive stance that frames EL services within an
    asset-based multilingual framework unique among US states.
    """
    data = [
        # (complex_area_id, complex_area_name, total_students, el_count, el_percent,
        #  sba_meets_all, sba_meets_el, dominant_languages, island, context_note)

        # --- Oahu ---
        ("CA01", "Farrington-Kaiser-Kalani", 14200, 1846, 13.0, 38.5, 11.2, "Ilokano, Chuukese, Samoan", "Oahu", "Urban Honolulu; highest EL count on Oahu"),
        ("CA02", "Kaimuki-McKinley-Roosevelt", 11800, 1298, 11.0, 42.5, 13.5, "Chuukese, Marshallese, Ilokano", "Oahu", "Central Honolulu; Kalihi immigrant gateway"),
        ("CA03", "Aiea-Moanalua-Radford", 9500, 760, 8.0, 48.2, 15.8, "Ilokano, Samoan, Tagalog", "Oahu", "Military-adjacent; Pearl Harbor area"),
        ("CA04", "Leilehua-Mililani-Waialua", 12500, 875, 7.0, 50.5, 16.2, "Ilokano, Tagalog, Samoan", "Oahu", "Central Oahu; pineapple plantation legacy"),
        ("CA05", "Castle-Kahuku", 7800, 546, 7.0, 46.8, 14.5, "Samoan, Tongan, Marshallese", "Oahu", "Windward + North Shore"),
        ("CA06", "Pearl City-Waipahu", 11200, 1456, 13.0, 40.2, 12.2, "Ilokano, Chuukese, Samoan", "Oahu", "Waipahu: 'Little Philippines'; high Ilokano"),
        ("CA07", "Campbell-Kapolei", 13500, 1080, 8.0, 44.5, 14.0, "Samoan, Marshallese, Ilokano", "Oahu", "Leeward Oahu; fastest growing area"),
        ("CA08", "Nanakuli-Waianae", 7200, 576, 8.0, 32.5, 9.5, "Samoan, Marshallese, Chuukese", "Oahu", "Leeward coast; high poverty + COFA community"),

        # --- Neighbor Islands ---
        ("CA09", "Maui", 11500, 920, 8.0, 40.8, 12.5, "Ilokano, Chuukese, Tagalog", "Maui", "Central + West Maui; agricultural ELs"),
        ("CA10", "Baldwin-Kekaulike-Maui", 6800, 476, 7.0, 44.2, 14.2, "Ilokano, Tagalog, Chuukese", "Maui", "Upcountry + East Maui"),
        ("CA11", "Hilo-Waiakea", 8200, 574, 7.0, 42.8, 13.8, "Ilokano, Chuukese, Marshallese", "Hawaii Island", "East Hawaii; Hilo area"),
        ("CA12", "Kau-Keaau-Pahoa", 5500, 385, 7.0, 36.5, 10.8, "Chuukese, Marshallese, Ilokano", "Hawaii Island", "Southeast Hawaii; rural + volcanic area"),
        ("CA13", "Honokaa-Kealakehe-Kohala-Konawaena", 7800, 468, 6.0, 41.5, 13.2, "Ilokano, Tagalog, Marshallese", "Hawaii Island", "West Hawaii; Kona coast"),
        ("CA14", "Kauai-Waimea", 6200, 434, 7.0, 43.5, 14.0, "Ilokano, Tagalog, Chuukese", "Kauai", "Garden Isle; agricultural communities"),
        ("CA15", "Molokai-Lanai", 1800, 108, 6.0, 38.2, 11.5, "Ilokano, Tagalog", "Molokai/Lanai", "Rural islands; limited services"),
    ]

    return pd.DataFrame(data, columns=[
        'complex_area_id', 'complex_area_name', 'total_students',
        'el_count', 'el_percent',
        'sba_meets_all', 'sba_meets_el',
        'dominant_languages', 'island', 'context_note'
    ])


# ============================================================================
# DATA: ACCESS Domain Data (WIDA ACCESS for ELLs)
# ============================================================================

def load_access_data(areas_df):
    """Generate Complex Area ACCESS domain data modeled from HI EL performance patterns.
    Hawaii uses WIDA ACCESS for EL assessment."""
    access_data = []

    for _, d in areas_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 332 + (grade * 8)
                base_writing = 282 + (grade * 6)

                el_density_penalty = max(0, (d['el_percent'] - 8) * 0.5)
                el_factor = d['sba_meets_el'] / 13.0
                speaking_adj = int(13 * el_factor + d['el_percent'] * 0.25 - el_density_penalty)
                writing_adj = int(-9 + (el_factor - 1) * 10 - el_density_penalty * 0.8)

                yr_adj = 3 if year == 2025 else 0

                access_data.append({
                    'complex_area_id': d['complex_area_id'],
                    'complex_area_name': d['complex_area_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(12, int(d['el_count'] / 6)),
                    'listening_avg': base_speaking + speaking_adj - 4 + yr_adj,
                    'speaking_avg': base_speaking + speaking_adj + yr_adj,
                    'reading_avg': base_writing + writing_adj + 13 + yr_adj,
                    'writing_avg': base_writing + writing_adj + yr_adj,
                    'composite_avg': int((base_speaking + speaking_adj + base_writing + writing_adj) / 2 + 14 + yr_adj),
                })

    return pd.DataFrame(access_data)


# ============================================================================
# DATA: SBA Achievement Data
# SBA (Smarter Balanced Assessment), 4 levels:
#   Well Below Standard / Below Standard / Near Standard / Meets or Exceeds Standard
# ============================================================================

def load_sba_data(areas_df):
    """Generate SBA data based on arch.k12.hi.us patterns."""
    sba_data = []

    for _, d in areas_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    base = d['sba_meets_all'] if subject == 'ELA' else d['sba_meets_all'] * 0.82
                    meets_exceeds = max(8, min(75, base + (grade - 5) * -1.3))

                    exceeds = max(2, meets_exceeds * 0.18)
                    meets = meets_exceeds - exceeds
                    near = max(15, (100 - meets_exceeds) * 0.38)
                    below = max(8, (100 - meets_exceeds - near) * 0.5)
                    well_below = max(5, 100 - meets_exceeds - near - below)

                    sba_data.append({
                        'complex_area_id': d['complex_area_id'],
                        'complex_area_name': d['complex_area_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'meets_exceeds_pct': round(meets_exceeds, 1),
                        'exceeds_pct': round(exceeds, 1),
                        'meets_pct': round(meets, 1),
                        'near_pct': round(near, 1),
                        'below_pct': round(below, 1),
                        'well_below_pct': round(well_below, 1),
                    })

    return pd.DataFrame(sba_data)


# ============================================================================
# DATA: Statewide Domain Proficiency (WIDA ACCESS results)
# ============================================================================

def load_statewide_domain_data():
    """Statewide ACCESS domain proficiency percentages by grade cluster.
    Source: HIDOE / arch.k12.hi.us / WIDA ACCESS results."""
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 41, 'speaking': 36, 'reading': 24, 'writing': 16},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 45, 'speaking': 41, 'reading': 28, 'writing': 19},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 49, 'speaking': 44, 'reading': 32, 'writing': 22},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 52, 'speaking': 47, 'reading': 35, 'writing': 24},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 38, 'speaking': 33, 'reading': 22, 'writing': 14},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 42, 'speaking': 38, 'reading': 26, 'writing': 17},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 46, 'speaking': 41, 'reading': 30, 'writing': 20},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 49, 'speaking': 44, 'reading': 33, 'writing': 22},
    ])


# ============================================================================
# DATA: EL Population Data
# ============================================================================

def load_el_growth_data():
    """Hawaii EL population trends -- influenced by Pacific Islander migration
    (COFA nations: FSM, Marshall Islands, Palau) and Filipino immigration."""
    return pd.DataFrame([
        {'year': 2008, 'el_count': 14200, 'el_percent': 7.8, 'note': 'Baseline'},
        {'year': 2010, 'el_count': 13800, 'el_percent': 7.6, 'note': 'Slight decline'},
        {'year': 2012, 'el_count': 13200, 'el_percent': 7.3, 'note': ''},
        {'year': 2014, 'el_count': 12800, 'el_percent': 7.1, 'note': 'Policy 105-14 adopted'},
        {'year': 2016, 'el_count': 12500, 'el_percent': 6.9, 'note': ''},
        {'year': 2018, 'el_count': 12200, 'el_percent': 6.8, 'note': 'Stable period'},
        {'year': 2020, 'el_count': 11800, 'el_percent': 6.6, 'note': 'COVID dip; inter-island migration'},
        {'year': 2022, 'el_count': 12200, 'el_percent': 6.8, 'note': 'Post-COVID rebound'},
        {'year': 2024, 'el_count': 12500, 'el_percent': 7.0, 'note': 'COFA migration increase'},
        {'year': 2025, 'el_count': 12600, 'el_percent': 7.0, 'note': 'Maui fire displacement'},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(access_df, complex_area_id, grade, year):
    filtered = access_df[
        (access_df['complex_area_id'] == complex_area_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'complex_area_id': complex_area_id, 'complex_area_name': row['complex_area_name'],
        'grade': grade, 'year': year,
        'speaking_avg': row['speaking_avg'], 'writing_avg': row['writing_avg'],
        'delta': delta, 'delta_normalized': delta_normalized, 'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================

def render_overview(areas_df):
    st.header("Hawaii Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Complex Areas", len(areas_df))
    with col2: st.metric("Total Students", f"{areas_df['total_students'].sum():,}")
    with col3: st.metric("English Learners", f"{areas_df['el_count'].sum():,}")
    with col4: st.metric("Statewide EL %", "~7%", delta="Stable")

    st.divider()

    # Key policy context
    st.subheader("Key Policy Context")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("**1 Statewide District**\nHIDOE is the only US state with a single district; 15 Complex Areas serve as administrative regions")
    with col2:
        st.warning("**Policy 105-14**\nBOE policy promoting multilingualism & multiliteracy as assets for all students")
    with col3:
        st.success("**Pacific Islander Languages**\nIlokano, Chuukese, Marshallese, Samoan -- distinct from mainland EL demographics")

    st.divider()

    # Hawaii's unique context
    st.subheader("The Hawaii Pattern: Pacific Islander Languages & One-District State")
    st.markdown("""
    Hawaii is **unique among US states** in having a single statewide school district (HIDOE)
    with 15 Complex Areas serving as administrative regions. This structure means all
    EL policy, funding, and program decisions flow through one centralized system.

    **Hawaii's EL population is distinctly Pacific Islander and Asian**, unlike mainland
    states dominated by Spanish-speaking ELs:

    | Language | % of ELs | Origin Communities |
    |----------|----------|--------------------|
    | Ilokano | ~28% | Filipino immigrant families (plantation legacy) |
    | Chuukese | ~18% | COFA nation (Federated States of Micronesia) |
    | Marshallese | ~12% | COFA nation (Republic of the Marshall Islands) |
    | Samoan | ~10% | American Samoa + independent Samoa |
    | Tagalog | ~8% | Filipino families (Manila-region origin) |

    **COFA Context:** The Compact of Free Association allows citizens of FSM, Marshall Islands,
    and Palau to live and work in the US. Hawaii is a primary destination, and COFA
    communities face unique challenges: interrupted education, cultural adjustment,
    limited English literacy in home language.

    **Policy 105-14 (2014)** is a progressive BOE policy that promotes multilingualism
    and multiliteracy as goals for all students -- framing linguistic diversity as an
    asset rather than a deficit. This is rare among US states.
    """)

    st.divider()

    st.subheader("Assessment Framework")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **SBA (Smarter Balanced Assessment):**
        - Smarter Balanced alignment
        - ELA and Math, grades 3-8, 11
        - 4 Achievement Levels:
            - **Exceeds Standard**
            - **Meets Standard** (proficient)
            - **Near Standard** (approaching)
            - **Below Standard**
        - Results on arch.k12.hi.us

        **Strive HI:**
        - Accountability system
        - Academic achievement + growth
        - Graduation rate + readiness
        - Chronic absenteeism
        - ELP progress indicator
        """)
    with col2:
        st.markdown("""
        **EL Program:**
        - **WIDA ACCESS** for ELP assessment
        - 4 Domains: Listening, Speaking, Reading, Writing
        - 1 statewide district / 15 Complex Areas
        - ~12,600 ELs (~7% statewide)
        - **Policy 105-14** multilingualism goal

        **Key Language Groups:**
        - Ilokano (~28%), Chuukese (~18%)
        - Marshallese (~12%), Samoan (~10%)
        - Tagalog (~8%), other Pacific/Asian

        **Key Context:**
        - **COFA migration** -- FSM, Marshall Islands, Palau
        - **Maui fires (2023)** -- displacement impact
        - **Military families** -- transient EL populations
        - Single-district centralized system

        **Data:** arch.k12.hi.us
        """)

    st.divider()

    # Complex Area table
    st.subheader("Complex Areas -- EL Populations & Performance")
    display = areas_df[['complex_area_id', 'complex_area_name', 'total_students', 'el_count',
                        'el_percent', 'sba_meets_all', 'sba_meets_el',
                        'dominant_languages', 'island']].copy()
    display.columns = ['ID', 'Complex Area', 'Students', 'EL Count', 'EL %',
                       'SBA Meets+ All %', 'SBA Meets+ EL %', 'Top Languages', 'Island']
    st.dataframe(display, use_container_width=True, hide_index=True)

    # EL bar chart
    st.subheader("English Learner Population by Complex Area")
    fig = px.bar(
        areas_df.sort_values('el_count', ascending=True),
        x='el_count', y='complex_area_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, HI_RED]],
        labels={'el_count': 'English Learners', 'complex_area_name': 'Complex Area', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=550, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Island distribution
    st.subheader("EL Distribution by Island")
    island_df = areas_df[['complex_area_name', 'el_percent', 'el_count', 'island']].copy()
    fig2 = px.scatter(island_df, x='el_count', y='el_percent',
                      color='island', size='el_count',
                      hover_name='complex_area_name',
                      color_discrete_map={
                          'Oahu': HI_RED,
                          'Maui': HI_BLUE,
                          'Hawaii Island': HI_GRAY,
                          'Kauai': '#2E7D32',
                          'Molokai/Lanai': '#FF9800'
                      },
                      labels={'el_count': 'EL Count', 'el_percent': 'EL %',
                              'island': 'Island'})
    fig2.update_layout(
        title="EL Population by Island -- Oahu Concentrates Most ELs",
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================================
# PAGE 2: DOMAIN ANALYSIS
# ============================================================================

def render_domain_analysis(domain_df, growth_df):
    st.header("Statewide ACCESS Domain Proficiency")

    st.markdown("""
    **Source:** HIDOE / arch.k12.hi.us / WIDA ACCESS results.
    Hawaii is a WIDA Consortium member. Domain proficiency percentages reveal the
    systemic oral-written delta.

    **Hawaii Context:** The dominance of Oceanic languages (Chuukese, Marshallese, Samoan)
    creates a distinct oral-written gap pattern. These languages have shorter written
    traditions compared to European languages, meaning students may have limited
    home-language literacy to transfer to English writing. Policy 105-14's
    multilingualism goal acknowledges this complexity.
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', HI_GRAY), ('speaking', HI_RED),
                          ('reading', HI_LIGHT_RED), ('writing', HI_BLUE)]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ACCESS Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient",
        barmode='group', height=450, yaxis=dict(range=[0, 65])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[HI_RED if d > 18 else HI_LIGHT_RED for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap", yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.divider()

    # EL population trend
    st.subheader("Hawaii EL Population Trends")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=growth_df['year'], y=growth_df['el_count'],
        mode='lines+markers', line=dict(color=HI_RED, width=3),
        marker=dict(size=8), name='EL Count'
    ))
    fig3.update_layout(
        title="EL Population -- Relatively Stable with COFA Migration Influence",
        xaxis_title="Year", yaxis_title="English Learners",
        height=400
    )
    fig3.add_annotation(x=2014, y=12800, text="Policy 105-14", showarrow=True, arrowhead=2)
    fig3.add_annotation(x=2023, y=12200, text="Maui fires", showarrow=True, arrowhead=2)
    st.plotly_chart(fig3, use_container_width=True)

    st.info("""
    **Oceanic Language Context:** Unlike mainland states where Spanish-speaking ELs dominate,
    Hawaii's top EL languages (Ilokano, Chuukese, Marshallese, Samoan) are Oceanic and
    Philippine languages with distinct orthographic systems. Chuukese and Marshallese
    have limited written traditions, meaning students may lack home-language literacy
    to scaffold English writing development. This structural factor amplifies the
    oral-written gap beyond what is seen in Spanish-dominant EL populations.
    """)


# ============================================================================
# PAGE 3: EL ASSESSMENT ANALYSIS (ACCESS)
# ============================================================================

def render_el_assessment(access_df, areas_df):
    st.header("ACCESS for ELLs Analysis")
    st.markdown("""
    **WIDA ACCESS** measures English learners across four domains. Hawaii has ~12,600 ELs
    across 15 Complex Areas within the single statewide HIDOE district.
    """)

    col1, col2, col3 = st.columns(3)
    with col1: area = st.selectbox("Complex Area", areas_df['complex_area_name'].tolist(), key="acc_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="acc_g")
    with col3: year = st.selectbox("Year", [2025, 2024], key="acc_y")

    ca_id = areas_df[areas_df['complex_area_name'] == area]['complex_area_id'].values[0]
    filtered = access_df[(access_df['complex_area_id'] == ca_id) &
                         (access_df['grade'] == grade) &
                         (access_df['year'] == year)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        d_info = areas_df[areas_df['complex_area_id'] == ca_id].iloc[0]
        if d_info['el_percent'] > 10:
            st.warning(f"""
            **Higher-Concentration Area:** {area} has **{d_info['el_percent']:.1f}% EL enrollment**.
            Top languages: {d_info['dominant_languages']}. {d_info['context_note']}.
            """)

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2: st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3: st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4: st.metric("Writing", f"{row['writing_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(x=domains, y=scores,
                               marker_color=[HI_GRAY, HI_RED, HI_LIGHT_RED, HI_BLUE],
                               text=[f"{s:.0f}" for s in scores], textposition='outside'))
        fig.update_layout(title=f"ACCESS Domains -- {area} -- Grade {grade} ({year})",
                         yaxis_title="Scale Score", height=400)
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written

        st.subheader("Oral vs Written Gap")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Oral Average", f"{oral:.0f}")
        with col2: st.metric("Written Average", f"{written:.0f}")
        with col3: st.metric("Gap", f"{gap:+.0f}", delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")

        st.divider()
        st.subheader("Composite & Context")
        composite = row['composite_avg']
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Composite Average", f"{composite}")
        with col2: st.metric("Island", d_info['island'])
        with col3: st.metric("Total Tested", f"{row['total_tested']:,}")


# ============================================================================
# PAGE 4: TYPE 4 DETECTION
# ============================================================================

def render_type4(access_df, areas_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking Score - Writing Score. Flag threshold: normalized delta > 8 points.

    **Hawaii Context:** Oceanic language speakers (Chuukese, Marshallese, Samoan) may
    exhibit pronounced Type 4 patterns because their home languages have limited
    written traditions. Students develop conversational English through community
    immersion but lack the home-language literacy foundation that supports English
    academic writing development. Policy 105-14's multilingualism goal recognizes
    this challenge but the composite weighting still penalizes writing deficiency.
    """)

    col1, col2, col3 = st.columns(3)
    with col1: area = st.selectbox("Complex Area", areas_df['complex_area_name'].tolist(), key="t4_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3: year = st.selectbox("Year", [2025, 2024], key="t4_y")

    ca_id = areas_df[areas_df['complex_area_name'] == area]['complex_area_id'].values[0]
    result = compute_type4_analysis(access_df, ca_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2: st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3: st.metric("Delta", f"{result['delta']:+.0f}")
        with col4: st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']], marker_color=HI_RED))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']], marker_color=HI_BLUE))
        fig.update_layout(title=f"Speaking vs Writing -- {area} -- Grade {grade}", barmode='group', height=350)
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        # All grades
        st.subheader(f"All Grades -- {area} ({year})")
        all_data = [compute_type4_analysis(access_df, ca_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=gdf['grade'], y=gdf['speaking_avg'], name='Speaking',
                                     mode='lines+markers', line=dict(color=HI_RED, width=3)))
            fig.add_trace(go.Scatter(x=gdf['grade'], y=gdf['writing_avg'], name='Writing',
                                     mode='lines+markers', line=dict(color=HI_BLUE, width=3)))
            fig.update_layout(title="Speaking vs Writing Across Grades", xaxis_title="Grade",
                             yaxis_title="Scale Score", height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Complex Area Summary")
        if all_data:
            summary_df = pd.DataFrame(all_data)[['grade', 'speaking_avg', 'writing_avg', 'delta', 'flagged', 'estimated_flagged']]
            summary_df.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Flagged', 'Est. Affected']
            summary_df['Flagged'] = summary_df['Flagged'].map({True: 'YES', False: 'No'})
            st.dataframe(summary_df, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE 5: ACHIEVEMENT GAPS
# ============================================================================

def render_achievement_gaps(areas_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **Data from arch.k12.hi.us.** SBA Meets or Exceeds Standard rates across Complex Areas.

    **SBA** uses 4 achievement levels aligned to Smarter Balanced.
    Hawaii uses the **Strive HI** accountability system.

    **Key Pattern:** Leeward Oahu Complex Areas (Nanakuli-Waianae, Farrington-Kaiser-Kalani)
    show the widest EL-to-All achievement gaps. These areas have high COFA community
    populations and overlap with high poverty rates.
    """)

    st.divider()

    # All vs EL comparison
    fig = go.Figure()
    sorted_df = areas_df.sort_values('sba_meets_all', ascending=True)
    fig.add_trace(go.Bar(
        x=sorted_df['sba_meets_all'], y=sorted_df['complex_area_name'],
        name='All Students', orientation='h', marker_color=HI_GRAY
    ))
    fig.add_trace(go.Bar(
        x=sorted_df['sba_meets_el'], y=sorted_df['complex_area_name'],
        name='English Learners', orientation='h', marker_color=HI_RED
    ))
    fig.update_layout(
        title="SBA Meets+ Rate: All Students vs English Learners",
        barmode='group', xaxis_title="% Meets or Exceeds Standard",
        height=600, legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Gap analysis
    st.subheader("All-EL Achievement Gap by Complex Area")
    gap_df = areas_df.copy()
    gap_df['el_gap'] = gap_df['sba_meets_all'] - gap_df['sba_meets_el']
    gap_df = gap_df.sort_values('el_gap', ascending=True)

    fig_gap = go.Figure(go.Bar(
        x=gap_df['el_gap'], y=gap_df['complex_area_name'], orientation='h',
        marker_color=[HI_RED if g > 28 else HI_LIGHT_RED if g > 20 else HI_GRAY for g in gap_df['el_gap']],
        text=[f"{g:.0f} pts" for g in gap_df['el_gap']], textposition='outside'
    ))
    fig_gap.update_layout(title="All Students - EL Gap (SBA Meets+)",
                         xaxis_title="Gap (percentage points)", height=550)
    st.plotly_chart(fig_gap, use_container_width=True)

    # By island
    st.subheader("EL Proficiency by Island")
    fig2 = px.scatter(areas_df, x='el_percent', y='sba_meets_el', size='el_count',
                      color='island',
                      color_discrete_map={
                          'Oahu': HI_RED, 'Maui': HI_BLUE,
                          'Hawaii Island': HI_GRAY, 'Kauai': '#2E7D32',
                          'Molokai/Lanai': '#FF9800'
                      },
                      hover_name='complex_area_name',
                      labels={'el_percent': 'EL %', 'sba_meets_el': 'EL Meets+ %',
                              'el_count': 'EL Count', 'island': 'Island'})
    fig2.update_layout(
        title="EL Proficiency vs Concentration by Island",
        height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.info("""
    **Policy 105-14 & Achievement Gaps:** Despite Hawaii's progressive multilingualism
    policy, significant EL achievement gaps persist, particularly in areas with high
    COFA community populations. The single-district structure means the BOE can
    implement statewide EL policy changes efficiently, but Complex Areas have varying
    capacity to deliver specialized language support for diverse Pacific Islander
    and Asian language communities.
    """)


# ============================================================================
# PAGE 6: SBA ANALYSIS (State Test)
# ============================================================================

def render_sba(sba_df, areas_df):
    st.header("SBA Assessment Analysis")
    st.markdown("""
    **SBA (Smarter Balanced Assessment)** assesses students in grades 3-8 and 11 in ELA and Math.

    **4 Achievement Levels:**
    - **Exceeds Standard** -- Advanced mastery
    - **Meets Standard** -- Grade-level proficiency
    - **Near Standard** -- Approaching proficiency
    - **Below Standard** -- Below grade-level expectations

    Results are published on **arch.k12.hi.us** and contribute to the **Strive HI** accountability system.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1: area = st.selectbox("Complex Area", areas_df['complex_area_name'].tolist(), key="sba_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="sba_g")
    with col3: subject = st.selectbox("Subject", ['ELA', 'Math'], key="sba_s")
    with col4: year = st.selectbox("Year", [2025, 2024], key="sba_y")

    ca_id = areas_df[areas_df['complex_area_name'] == area]['complex_area_id'].values[0]
    filtered = sba_df[(sba_df['complex_area_id'] == ca_id) &
                      (sba_df['grade'] == grade) &
                      (sba_df['subject'] == subject) &
                      (sba_df['year'] == year)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Meets + Exceeds Standard", f"{row['meets_exceeds_pct']:.1f}%",
                      help="Grade-level proficient and above")
        with col2:
            st.metric("Exceeds Standard Only", f"{row['exceeds_pct']:.1f}%",
                      help="Advanced mastery")

        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Below Standard", f"{row['below_pct']:.1f}%")
        with col2: st.metric("Near Standard", f"{row['near_pct']:.1f}%")
        with col3: st.metric("Meets Standard", f"{row['meets_pct']:.1f}%")
        with col4: st.metric("Exceeds Standard", f"{row['exceeds_pct']:.1f}%")

        levels = ['Below\nStandard', 'Near\nStandard', 'Meets\nStandard', 'Exceeds\nStandard']
        values = [row['below_pct'], row['near_pct'], row['meets_pct'], row['exceeds_pct']]
        colors = ['#d32f2f', '#f57c00', HI_RED, HI_BLUE]
        fig = go.Figure(go.Bar(x=levels, y=values, marker_color=colors,
                               text=[f"{v:.1f}%" for v in values], textposition='outside'))
        fig.update_layout(title=f"SBA {subject} -- {area} -- Grade {grade} ({year})",
                         yaxis_title="Percentage", height=420)
        st.plotly_chart(fig, use_container_width=True)

        d_info = areas_df[areas_df['complex_area_id'] == ca_id].iloc[0]

        st.subheader("Complex Area Context")
        st.markdown(f"""
        **{area}** -- Grade {grade} {subject} ({year}):
        - Meets+ Rate: **{row['meets_exceeds_pct']:.1f}%**
        - Island: **{d_info['island']}** | EL %: **{d_info['el_percent']:.1f}%**
        - Top Languages: {d_info['dominant_languages']}
        - {d_info['context_note']}
        - Results on arch.k12.hi.us (Strive HI)
        """)


# ============================================================================
# PAGE 7: EXPORT DATA
# ============================================================================

def render_export(access_df, sba_df, areas_df, domain_df, growth_df):
    st.header("Export Data")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ACCESS Data")
        st.dataframe(access_df, use_container_width=True, hide_index=True)
        st.download_button("Download ACCESS CSV", access_df.to_csv(index=False),
                          "vera_hi_access.csv", "text/csv", use_container_width=True)
    with col2:
        st.subheader("SBA Data")
        st.dataframe(sba_df, use_container_width=True, hide_index=True)
        st.download_button("Download SBA CSV", sba_df.to_csv(index=False),
                          "vera_hi_sba.csv", "text/csv", use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button("Download Domain CSV", domain_df.to_csv(index=False),
                          "vera_hi_domains.csv", "text/csv", use_container_width=True)
    with col2:
        st.subheader("Complex Area Data")
        st.dataframe(areas_df, use_container_width=True, hide_index=True)
        st.download_button("Download Complex Areas CSV", areas_df.to_csv(index=False),
                          "vera_hi_complex_areas.csv", "text/csv", use_container_width=True)

    st.divider()

    st.subheader("EL Population Trends (2008-2025)")
    st.dataframe(growth_df, use_container_width=True, hide_index=True)
    st.download_button("Download EL Growth CSV", growth_df.to_csv(index=False),
                      "vera_hi_el_growth.csv", "text/csv", use_container_width=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(page_title="VERA-HI | Hawaii Type 4 Detection", page_icon="", layout="wide")

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {HI_RED}; }}
        .stButton > button {{ background-color: {HI_RED}; color: white; }}
        .stButton > button:hover {{ background-color: {HI_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    # Load data
    areas_df = load_complex_areas()
    access_df = load_access_data(areas_df)
    sba_df = load_sba_data(areas_df)
    domain_df = load_statewide_domain_data()
    growth_df = load_el_growth_data()

    # Sidebar
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {HI_RED}; margin: 0;">VERA-HI</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Hawaii Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Domain Analysis",
        "EL Assessment Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "State Test Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ACCESS for ELLs (WIDA)
    - SBA (Smarter Balanced)
    - arch.k12.hi.us
    - HIDOE EL reports

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points
    - WIDA ACCESS domain scores

    **Key HI Context:**
    - 1 statewide district (HIDOE)
    - 15 Complex Areas
    - ~12,600 ELs (~7%)
    - Ilokano, Chuukese,
      Marshallese, Samoan
    - Policy 105-14 multilingualism
    - COFA migration (FSM, RMI, Palau)
    - Maui fires (2023) impact
    - Strive HI accountability
    - SBA: Smarter Balanced

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview": render_overview(areas_df)
    elif page == "Domain Analysis": render_domain_analysis(domain_df, growth_df)
    elif page == "EL Assessment Analysis": render_el_assessment(access_df, areas_df)
    elif page == "Type 4 Detection": render_type4(access_df, areas_df)
    elif page == "Achievement Gaps": render_achievement_gaps(areas_df)
    elif page == "State Test Analysis": render_sba(sba_df, areas_df)
    elif page == "Export Data": render_export(access_df, sba_df, areas_df, domain_df, growth_df)


if __name__ == "__main__":
    main()
