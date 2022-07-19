terraform {
  backend "s3" {
    bucket  = "mvana-account-terraform"
    key     = "dijon/state"
    region  = "us-east-1"
    profile = "mvana"
  }
}

provider "oci" {
  region              = var.region
  config_file_profile = var.config_file_profile
}

terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 4.84.0"
    }
  }
}
