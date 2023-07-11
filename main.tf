terraform {
    required_version = ">= 1.0"
    backend "local" {} # Can change from "local" to "gcs" (for google) or "s3" (for aws)
    required_providers {
        google = {
            source = "hashicorp/google"
        }
    }
}


provider "google" {
    project = var.project
    region = var.region
    // credentials = file(var.credentials) # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}


# Cloud Storage Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data_lake_bucket" {
    name = "${local.data_lake_bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
    location = var.region

    # Optional, but recommended settings:
    storage_class = var.storage_class
    uniform_bucket_level_access = True

    versioning {
    enabled = True
    }

    lifecycle_rule {
        action {
            type = "delete"
        }
        conditon {
            age = 30 // days
        }
    }

    force_destroy = True
}

# DWH on BigQuery
# Ref https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
    dataset_id = var.BQK_DATASET
    project = var.project
    location = var.region
}