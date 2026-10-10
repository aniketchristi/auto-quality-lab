import json
import pytest
from auto_quality.review_store import load_packet, save_review


@pytest.fixture
def packet_path(tmp_path):
    path = tmp_path / 'packet.json'
    path.write_text(json.dumps({'seed':'test', 'reviews':[
        {'review_id':'one','narrative':'Synthetic test narrative','review_status':'pending'},
        {'review_id':'two','narrative':'Another test narrative','review_status':'pending'}]}))
    return path


def values():
    return dict(symptom_code='steering resistance',component_consistent='uncertain',
                evidence_specificity='vague',reporting_delay_note='',review_note='Synthetic assessment')


def test_save_preserves_other_evidence_and_rejects_stale_edit(packet_path):
    before, revision = load_packet(packet_path)
    save_review(packet_path, revision, 'one', values())
    after, new_revision = load_packet(packet_path)
    assert after['reviews'][0]['review_status'] == 'completed'
    assert after['reviews'][0]['narrative'] == before['reviews'][0]['narrative']
    assert after['reviews'][1] == before['reviews'][1]
    assert new_revision != revision
    with pytest.raises(ValueError, match='another session'):
        save_review(packet_path, revision, 'two', values())


def test_invalid_review_does_not_change_packet(packet_path):
    original = packet_path.read_bytes()
    _, revision = load_packet(packet_path)
    invalid = values()
    invalid['symptom_code'] = ' '
    with pytest.raises(ValueError, match='symptom'):
        save_review(packet_path, revision, 'one', invalid)
    assert packet_path.read_bytes() == original
