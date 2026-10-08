import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent / 'src'))
import pandas as pd
import plotly.express as px
import streamlit as st
from auto_quality.analysis import read, review_queue, last_complete_month
from auto_quality.common import ROOT
from auto_quality.quality import date_profile

st.set_page_config(page_title='Auto Quality Lab',page_icon=None,layout='wide')
st.title('Auto Quality Lab')
st.caption('Public owner reports · Investigation support · Initial passenger-car cohort')
st.warning('Complaint counts are not failure rates. Reports are allegations; recall context does not establish a shared defect or VIN-level applicability.')
try:
    vehicles = read('SELECT * FROM vehicles ORDER BY make,model,model_year')
except Exception:
    st.error('Database unavailable. Run ./scripts/start-db.sh, then the pipeline. See README.md.')
    st.stop()
if vehicles.empty:
    st.info('No data loaded yet. Run the ingestion command in README.md.')
    st.stop()
with st.sidebar:
    st.header('Analysis scope')
    families = sorted((vehicles.make + ' ' + vehicles.model).unique())
    selected = st.multiselect('Model families',families,default=families)
    years = st.multiselect('Model years',sorted(vehicles.model_year.unique()),default=sorted(vehicles.model_year.unique()))
    as_of = st.date_input('Receipt cutoff',value=last_complete_month(),max_value=last_complete_month())
    window = st.selectbox('Comparison window (days)',[90,180,365])
    minimum = st.slider('Minimum recent reports per group',5,50,10)
    st.caption('Two adjacent equal-length windows. Flags require ≥5 additional reports and ≥2× baseline, or a zero baseline. These are screening rules, not statistical significance tests.')
    st.caption('Historical views use current revised records. They are not exact historical source snapshots.')

v = vehicles[(vehicles.make+' '+vehicles.model).isin(selected)&vehicles.model_year.isin(years)]
keys = v.vehicle_key.tolist()
details = read('SELECT * FROM complaint_detail WHERE vehicle_key=ANY(%s) AND received_date<=%s',(keys,as_of))
recalls = read('SELECT * FROM recall_detail WHERE vehicle_key=ANY(%s) AND report_date<=%s',(keys,as_of))
unique = details.drop_duplicates('odi_number')
metrics = st.columns(4)
metrics[0].metric('Distinct complaints',len(unique))
metrics[1].metric('Model-years',len(v))
metrics[2].metric('Recall campaigns',recalls.campaign_number.nunique())
severe = unique[(unique.crash==True)|(unique.fire==True)|(unique.injuries.fillna(0)>0)|(unique.deaths.fillna(0)>0)]
metrics[3].metric('Severe reports',len(severe))
st.caption('Severe reports mention crash, fire, injury, or death. These outcomes are owner-reported.')
manifest = ROOT / 'data/processed/latest_manifest.json'
if manifest.exists():
    import json
    m=json.loads(manifest.read_text())
    from datetime import datetime
    from zoneinfo import ZoneInfo
    source_time=min(e['retrieved_at'] for e in m['files'])
    source_display=datetime.fromisoformat(source_time).astimezone(ZoneInfo('America/Los_Angeles')).strftime('%b %d, %Y · %I:%M %p %Z')
    st.caption(f'Source download: {source_display} · {len(m["files"])} API responses')
overview, investigation, sources = st.tabs(['Reporting trends','Investigation workbench','Data quality & sources'])
with overview:
    monthly = read('SELECT * FROM monthly_reporting WHERE vehicle_key=ANY(%s) AND month<=%s',(keys,as_of))
    # A historical cutoff can fall mid-month: derive the chart from filtered detail records.
    if not details.empty:
        chart=details.copy()
        chart['month']=pd.to_datetime(chart.received_date).dt.to_period('M').dt.to_timestamp()
        chart['family']=chart.make+' '+chart.model
        chart=chart.groupby(['month','family']).odi_number.nunique().reset_index(name='complaints')
        months=pd.date_range(chart.month.min(),pd.Timestamp(as_of).replace(day=1),freq='MS')
        grid=pd.MultiIndex.from_product([months,chart.family.unique()],names=['month','family'])
        chart=chart.set_index(['month','family']).reindex(grid,fill_value=0).reset_index()
        st.plotly_chart(px.line(chart,x='month',y='complaints',color='family',labels={'complaints':'Distinct reports received','month':'Receipt month'}),width='stretch')
    queue=review_queue(as_of,window,minimum)
    if not queue.empty:
        queue=queue[queue.vehicle_key.isin(keys)]
    st.subheader('Component groups for review')
    st.caption('A complaint can mention several components, so rows must not be summed to obtain total complaints. Model comparisons are descriptive, not reliability rankings.')
    st.dataframe(queue.drop(columns=['vehicle_key'],errors='ignore'),hide_index=True,width='stretch')
    st.download_button('Download review queue',queue.to_csv(index=False),'review_queue.csv','text/csv')
with investigation:
    options=v.vehicle_key.tolist()
    if options:
        chosen=st.selectbox('Model-year',options)
        evidence=read('SELECT * FROM component_detail WHERE vehicle_key=%s AND received_date<=%s ORDER BY received_date DESC',(chosen,as_of))
        components=['All components']+sorted(evidence.component.unique())
        component=st.selectbox('Component',components)
        if component!='All components': evidence=evidence[evidence.component==component]
        evidence=evidence.drop_duplicates('odi_number')
        st.dataframe(evidence[['odi_number','received_date','incident_date','crash','fire','injuries','deaths']],hide_index=True,width='stretch')
        if not evidence.empty:
            odi=st.selectbox('Read complaint',evidence.odi_number.tolist())
            st.write(evidence[evidence.odi_number==odi].iloc[0].narrative)
            make,model,year=chosen.split('|')
            from urllib.parse import urlencode
            st.link_button('Open official source records','https://api.nhtsa.gov/complaints/complaintsByVehicle?'+urlencode({'make':make,'model':model,'modelYear':year}))
        st.subheader('Recall context for this model-year')
        st.caption('Listed by model/year association, without an inferred complaint-to-campaign match. Consult campaign documents for affected build dates and variants.')
        for row in recalls[recalls.vehicle_key==chosen].itertuples():
            with st.expander(f'{row.campaign_number} · {row.report_date} · {row.component}'):
                st.write(row.summary)
                st.write('Consequence: '+(row.consequence or 'Not provided'))
                st.write('Remedy: '+(row.remedy or 'Not provided'))
                st.link_button('View official campaign record',f'https://api.nhtsa.gov/recalls/campaignNumber?campaignNumber={row.campaign_number}')
with sources:
    evaluation_file = ROOT / 'data/processed/screening_evaluation.json'
    if evaluation_file.exists():
        import json
        with st.expander('Historical screening workload evaluation'):
            evaluation = json.loads(evaluation_file.read_text())
            workload = pd.DataFrame(evaluation['workload'])
            st.caption('Fixed full-cohort evaluation: January 2023–September 2026 monthly cutoffs. These results are independent of the sidebar scope. Current revised records are used; this is not defect-detection accuracy.')
            workload_summary = workload.groupby(['window','minimum'], as_index=False).agg(
                mean_growth_groups=('growth_review_groups','mean'),
                maximum_growth_groups=('growth_review_groups','max'),
                mean_volume_groups=('volume_review_groups','mean'),
                maximum_volume_groups=('volume_review_groups','max'))
            st.dataframe(workload_summary.round(2), hide_index=True, width='stretch')
            chosen_workload = workload[(workload.window==window)&(workload.minimum==minimum)]
            if not chosen_workload.empty:
                st.plotly_chart(px.line(chosen_workload, x='cutoff',
                    y=['growth_review_groups','volume_review_groups'],
                    labels={'value':'Groups requiring review','cutoff':'Receipt cutoff','variable':'Rule'}), width='stretch')
            st.caption('Volume baseline flags every group at the same minimum count. An equal-budget baseline also ranks by recent volume. Neither baseline supplies confirmed defect labels. Overlapping monthly windows mean consecutive flags are not independent discoveries.')
    st.subheader('Model-label coverage')
    st.info('Exact-label cohort: separately named hybrids, hatchbacks, and performance variants are excluded. GOLF 2022 is absent from both audited official model lists; treat that row as unavailable label coverage, not evidence of zero failures.')
    coverage_file = ROOT / 'data/processed/coverage_audit.json'
    if coverage_file.exists():
        import json
        coverage = json.loads(coverage_file.read_text())
        coverage_rows = []
        for entry in coverage['files']:
            for family, labels in entry['family_candidates'].items():
                if entry['make'] + ' ' + family in selected and entry['year'] in years:
                    coverage_rows.append({'make':entry['make'], 'configured_model':family,
                        'year':entry['year'], 'list':'Complaints' if entry['issue_type']=='c' else 'Recalls',
                        'exact_label_present':entry['configured_labels_present'][family],
                        'related_labels':', '.join(labels)})
        st.dataframe(pd.DataFrame(coverage_rows), hide_index=True, width='stretch')
        st.caption('Substring candidates support manual coverage review. They do not establish every manufactured variant. This audit uses current model lists, independently of the selected receipt cutoff.')
    st.subheader('Reporting dates in the selected scope')
    date_records = read('SELECT odi_number,incident_date,received_date FROM complaint_detail WHERE vehicle_key=ANY(%s)', (keys,))
    date_summary, lag_distribution = date_profile(date_records, as_of)
    st.json(date_summary)
    st.dataframe(lag_distribution, hide_index=True, width='stretch')
    st.caption('Lag is receipt date minus incident date. Missing dates and negative intervals are excluded from lag statistics. Historical cutoffs use current revised records; later receipts are counted separately and excluded from lag statistics.')
    st.markdown('''Sources: [NHTSA datasets and APIs](https://www.nhtsa.gov/nhtsa-datasets-and-apis), [complaint dictionary](https://static.nhtsa.gov/odi/ffdd/cmpl/CMPL.txt).

The initial cohort uses exact API model labels. Hybrid, hatchback, performance, and other separately named variants may be omitted. Vehicle population and mileage exposure are unavailable in this model. Negative findings and low counts do not prove absence of defects.

Crash, fire, injury, and death fields are owner-reported indicators, not independently confirmed outcomes. Missing values remain unknown. Source snapshots, request URLs, retrieval timestamps, and SHA-256 hashes are stored locally. VINs are excluded from analytical tables and exports; narratives remain local.''')
    report=ROOT / 'data/processed/validation.json'
    if report.exists():
        st.json(json.loads(report.read_text()))
