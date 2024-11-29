terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "5.78.0"
    }
    archive = {
        source = "hashicorp/archive"
        version = "2.6.0"
    }
  }
}

provider "aws" {
    region = "us-east-1"
}