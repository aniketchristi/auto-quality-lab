CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id text PRIMARY KEY, started_at timestamptz NOT NULL,
    status text NOT NULL, manifest_path text NOT NULL
);
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_key text PRIMARY KEY, make text NOT NULL, model text NOT NULL,
    model_year integer NOT NULL CHECK (model_year BETWEEN 1900 AND 2100)
);
CREATE TABLE IF NOT EXISTS complaints (
    odi_number text PRIMARY KEY, incident_date date, received_date date,
    manufacturer text, crash boolean, fire boolean,
    injuries integer CHECK (injuries >= 0), deaths integer CHECK (deaths >= 0),
    narrative text NOT NULL, retrieved_at timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS complaint_vehicles (
    odi_number text REFERENCES complaints ON DELETE CASCADE,
    vehicle_key text REFERENCES vehicles,
    PRIMARY KEY (odi_number, vehicle_key)
);
CREATE TABLE IF NOT EXISTS complaint_components (
    odi_number text REFERENCES complaints ON DELETE CASCADE,
    component text NOT NULL, PRIMARY KEY (odi_number, component)
);
CREATE TABLE IF NOT EXISTS recalls (
    campaign_number text PRIMARY KEY, report_date date,
    component text, summary text, consequence text, remedy text,
    retrieved_at timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS recall_vehicles (
    campaign_number text REFERENCES recalls ON DELETE CASCADE,
    vehicle_key text REFERENCES vehicles,
    PRIMARY KEY (campaign_number, vehicle_key)
);
CREATE INDEX IF NOT EXISTS complaint_received_idx ON complaints(received_date);
CREATE INDEX IF NOT EXISTS complaint_vehicle_idx ON complaint_vehicles(vehicle_key);
CREATE OR REPLACE VIEW complaint_detail AS
SELECT c.*, v.vehicle_key, v.make, v.model, v.model_year
FROM complaints c JOIN complaint_vehicles cv USING (odi_number)
JOIN vehicles v USING (vehicle_key);
CREATE OR REPLACE VIEW component_detail AS
SELECT d.*, cc.component FROM complaint_detail d
JOIN complaint_components cc USING (odi_number);
CREATE OR REPLACE VIEW recall_detail AS
SELECT r.*, v.vehicle_key, v.make, v.model, v.model_year
FROM recalls r JOIN recall_vehicles rv USING (campaign_number)
JOIN vehicles v USING (vehicle_key);
CREATE OR REPLACE VIEW monthly_reporting AS
SELECT date_trunc('month', received_date)::date AS month,
       vehicle_key, make, model, model_year, count(DISTINCT odi_number) AS complaints,
       count(DISTINCT odi_number) FILTER (WHERE crash OR fire OR injuries > 0 OR deaths > 0) AS reported_severe
FROM complaint_detail WHERE received_date IS NOT NULL
GROUP BY 1,2,3,4,5;
