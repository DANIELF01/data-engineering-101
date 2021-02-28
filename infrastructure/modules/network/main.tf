resource "aws_vpc" "app_vpc" {
  cidr_block = var.cidr_block

  tags = {
    "Name" = var.env
  }
}

resource "aws_subnet" "public_subnet" {
  cidr_block = var.public_subnet_cidr
  vpc_id = aws_vpc.app_vpc.id
}