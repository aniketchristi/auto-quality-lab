from datetime import datetime

def parse_date(value, recall=False):
    if value in (None, '', '00000000'):
        return None
    formats = ['%Y-%m-%d', '%Y%m%d', '%d/%m/%Y' if recall else '%m/%d/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            pass
    raise ValueError(f'Unexpected source date: {value!r}')

def integer(value):
    if value is None or value == '':
        return None
    result = int(value)
    if result < 0:
        raise ValueError('Negative injury/death count')
    return result

def boolean(value):
    if value is None or value == '':
        return None
    if value in (True, 'Y', 'true', 'True', 1):
        return True
    if value in (False, 'N', 'false', 'False', 0):
        return False
    raise ValueError(f'Unexpected boolean: {value!r}')

def vehicle_key(make, model, year):
    return f'{str(make).strip().upper()}|{str(model).strip().upper()}|{int(year)}'

def complaint(record):
    components = sorted({x.strip().upper() for x in record.get('components', '').split(',') if x.strip()})
    return {
        'odi_number': str(record['odiNumber']),
        'incident_date': parse_date(record.get('dateOfIncident')),
        'received_date': parse_date(record.get('dateComplaintFiled')),
        'manufacturer': record.get('manufacturer'),
        'crash': boolean(record.get('crash')), 'fire': boolean(record.get('fire')),
        'injuries': integer(record.get('numberOfInjuries')),
        'deaths': integer(record.get('numberOfDeaths')),
        'narrative': record.get('summary') or '', 'components': components or ['UNSPECIFIED']
    }

def recall(record):
    return {
        'campaign_number': record['NHTSACampaignNumber'],
        'report_date': parse_date(record.get('ReportReceivedDate'), recall=True),
        'component': record.get('Component'), 'summary': record.get('Summary'),
        'consequence': record.get('Consequence'), 'remedy': record.get('Remedy')
    }
