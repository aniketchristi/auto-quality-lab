"""Manual review UI; only explicit user submissions create annotations."""
import streamlit as st
from .common import ROOT
from .review_store import load_packet, save_review


def render_review():
    st.subheader('Review the fixed complaint sample')
    st.caption('This packet has its own fixed cutoffs and is independent of sidebar filters. An annotation is a reading assessment, not a verified defect finding. Notes and narratives stay local.')
    path = ROOT / 'data/processed/manual_review_packet.json'
    if not path.exists():
        st.info('Create the packet with python scripts/prepare_review.py first.')
        return
    packet, revision = load_packet(path)
    records = packet['reviews']
    done = sum(r['review_status'] == 'completed' for r in records)
    st.progress(done / len(records) if records else 0, text=f'{done} of {len(records)} assignments reviewed')
    if not records:
        return
    pending_only = st.checkbox('Show pending assignments only', value=True, key='review_pending')
    visible = [r for r in records if not pending_only or r['review_status'] != 'completed']
    if not visible:
        st.success('No pending assignments. Clear the filter to inspect completed reviews.')
        return
    lookup = {r['review_id']:r for r in visible}
    selected_id = st.selectbox('Review assignment', list(lookup), key='review_assignment')
    revision_key = 'review_revision_' + selected_id
    if revision_key not in st.session_state:
        st.session_state[revision_key] = revision
    row = lookup[selected_id]
    st.caption(f"Selection: {row['stratum']} · Receipt: {row['received_date']} · Incident: {row['incident_date']}")
    st.write(row['narrative'])
    st.caption('Use short symptom descriptions. Keep names, contact information, addresses, and VINs out of notes. Use uncertain or insufficient when the account is ambiguous.')
    with st.form('review_' + selected_id):
        symptom = st.text_input('Symptom code', value=row.get('symptom_code') or '')
        assessments = ['uncertain', 'yes', 'no']
        consistency = st.selectbox('Narrative supports the listed component', assessments,
            index=assessments.index(row.get('component_consistent') or 'uncertain'))
        specificity_options = ['insufficient', 'vague', 'specific']
        specificity = st.selectbox('Evidence specificity', specificity_options,
            index=specificity_options.index(row.get('evidence_specificity') or 'insufficient'))
        delay = st.text_area('Reporting delay note', value=row.get('reporting_delay_note') or '')
        note = st.text_area('Review note', value=row.get('review_note') or '')
        confirmed = st.checkbox('I read this narrative and assessed these fields')
        submitted = st.form_submit_button('Save completed review locally')
        if submitted:
            if not confirmed:
                st.error('Confirm that you read the narrative before marking it completed.')
            else:
                try:
                    save_review(path, st.session_state[revision_key], selected_id, {
                        'symptom_code':symptom, 'component_consistent':consistency,
                        'evidence_specificity':specificity, 'reporting_delay_note':delay, 'review_note':note})
                    del st.session_state[revision_key]
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                    if 'another session' in str(error):
                        del st.session_state[revision_key]
                        st.caption('Reload this page and recheck the saved assessment before submitting again.')
