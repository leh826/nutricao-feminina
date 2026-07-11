# Bronze Layer
resource "aws_s3_bucket" "bronze_layer" {
  bucket = "projeto-nutricao-feminina-bronze"
}

# Silver Layer
resource "aws_s3_bucket" "silver_layer" {
  bucket = "projeto-nutricao-feminina-silver"
}

# Gold Layer
resource "aws_s3_bucket" "gold_layer" {
  bucket = "projeto-nutricao-feminina-gold"
}