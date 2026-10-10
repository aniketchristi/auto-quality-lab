import json
from streamlit.testing.v1 import AppTest
from auto_quality import review_ui


def test_review_requires_read_confirmation_and_persists(tmp_path, monkeypatch):
    folder = tmp_path / 'data/processed'
    folder.mkdir(parents=True)
    path = folder / 'manual_review_packet.json'
    path.write_text(json.dumps({'reviews':[{
        'review_id':'synthetic-one','stratum':'both','received_date':'2025-01-02',
        'incident_date':'2025-01-01','narrative':'Synthetic evidence for a UI test.',
        'review_status':'pending'}]}))
    monkeypatch.setattr(review_ui, 'ROOT', tmp_path)
    app = AppTest.from_string('from auto_quality.review_ui import render_review\nrender_review()').run()
    assert not app.exception
    app.text_input[0].set_value('steering resistance')
    app.button[0].click().run()
    assert app.error
    assert json.loads(path.read_text())['reviews'][0]['review_status'] == 'pending'
    app.checkbox[1].set_value(True)
    app.button[0].click().run()
    assert not app.exception
    saved = json.loads(path.read_text())['reviews'][0]
    assert saved['review_status'] == 'completed'
    assert saved['symptom_code'] == 'steering resistance'
    assert app.success
