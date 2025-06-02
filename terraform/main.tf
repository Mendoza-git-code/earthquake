terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.36.1"
    }
  }
}

provider "google" {
  project = "starlingcontacts-data-dev"
}

locals {
 gcp_region  = "asia-northeast1"
}