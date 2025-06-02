
resource "google_bigquery_dataset" "staging_temp" {
  dataset_id                  = "staging_temp"
  description                 = "Dataset for temporary (non-persisted) tables"
  location                    = local.gcp_region
  default_table_expiration_ms = 30 * 24 * 60 * 60 * 1000

  labels = {
    env = "default"
  }
}

