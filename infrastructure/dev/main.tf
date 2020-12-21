terraform {
  backend "s3" {
    bucket = "terraform-state-de101"
    key    = "dev/state.tf"
    region = "ap-southeast-2"
  }
}

provider "aws" {
  region = "ap-southeast-2"
}

module "network" {
  source = "../modules/network"
  cidr_block = "172.0.0.0/25"
  public_subnet_cidr = "172.0.0.0/28"
  env = "staging"
}

