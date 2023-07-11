locals {
    data_lake_bucket = "ga_storage"
}

variable "project" {
    description = "Google Analytics 360 Data"
    default = "dtc-de-project"
}

variable "region" {
    description = "Region for GCP resources. Choose as per your location:  https://cloud.google.com/about/locations"
    default = "europe-west3"
    type = string
}

variable "storage_class" {
    description = "Storage class type for your bucket. Check official docs for more information
    defaul = "STANDARD"
}

variable "BQ_DATASET" {
    description = "BigQuery Dataset that raw data (from GCS) will be writeen to"
    type = string
    defaul = "ga_data"
}