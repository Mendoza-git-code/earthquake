
resource "google_bigquery_dataset" "earthquake_model" {
  dataset_id                  = "earthquake_model"
  description                 = "Data model for earthquake data"
  location                    = local.gcp_region

  labels = {
    env = "default"
  }
}

resource "google_bigquery_table" "event_earthquake" {
  dataset_id                  = google_bigquery_dataset.earthquake_model.dataset_id
  table_id                    = "event_earthquake"
  deletion_protection         = true

  time_partitioning {
    field = "event_date"
    type = "DAY"
  }

  labels = {
    env = "default"
  }

  schema = <<EOF
[
  {
    "name": "event_date",
    "type": "DATE",
    "mode": "NULLABLE",
    "description": "Date of the event"
  },
  {
    "name": "event_time",
    "type": "TIME",
    "mode": "NULLABLE",
    "description": "Time of the event"
  },
  {
    "name": "magnitude",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Magnitude of the earthquake"
  },
  {
    "name": "location_desc",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Description of the earthquake location"
  },
  {
    "name": "latitude",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Latitude of the location"
  },
  {
    "name": "longitude",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Longitude of the location"
  },
  {
    "name": "depth",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Depth of the earthquake"
  },
  {
    "name": "geo",
    "type": "GEOGRAPHY",
    "mode": "NULLABLE",
    "description": "BigQuery geography attribute for the location"
  },
  {
    "name": "type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Type of the earthquake"
  },
  {
    "name": "url",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "URL link to detailed information"
  }
]
EOF

}