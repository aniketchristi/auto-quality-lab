"""Exercise the real database-backed app, including empty selections and historical cutoff."""
from datetime import date
from streamlit.testing.v1 import AppTest
from auto_quality.common import ROOT

app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
assert not app.exception, [e.message for e in app.exception]
assert len(app.metric)==4
assert int(app.metric[0].value)>0
print('Default app renders with four live metrics.')
app.multiselect[0].set_value([]).run()
assert not app.exception, [e.message for e in app.exception]
assert app.metric[0].value=='0'
print('Empty model selection renders without exceptions.')
app.multiselect[0].set_value(['HONDA CIVIC'])
app.date_input[0].set_value(date(2023,12,31)).run()
assert not app.exception, [e.message for e in app.exception]
print('Historical cutoff and single-family filter render without exceptions.')
