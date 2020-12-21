variable "cidr_block" {
  type = string
  description = "VPC CIDR block"
}

variable "public_subnet_cidr" {
  type = string
  description = "Public subnet CIDR"
}

variable "env" {
  type = string
  description = "Environment"
}