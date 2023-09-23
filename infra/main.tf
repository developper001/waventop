locals {
  dot_env_file_path = "../.env"
  dot_env_regex = "(?m:^\\s*([^#\\s]\\S*)\\s*=\\s*[\"']?(.*[^\"'\\s])[\"']?\\s*$)"
  dot_env = { for tuple in regexall(local.dot_env_regex, file(local.dot_env_file_path)) : tuple[0] => sensitive(tuple[1]) }
  AWS_ACCESS_KEY = local.dot_env["AWS_ACCESS_KEY"]
  AWS_SECRET_KEY = local.dot_env["AWS_SECRET_KEY"]
  AWS_REGION = local.dot_env["AWS_REGION"]
}

provider "aws" {
  access_key = local.AWS_ACCESS_KEY
  secret_key = local.AWS_SECRET_KEY
  region = local.AWS_REGION
}

# Bucket
resource "aws_s3_bucket" "waventopbucket" {
  bucket = "waventopbucket"
  force_destroy = true
}

# Access
resource "aws_s3_bucket_public_access_block" "waventopbucket" {
  bucket = aws_s3_bucket.waventopbucket.id
  block_public_acls = false
  block_public_policy = false
  ignore_public_acls = true
  restrict_public_buckets = false
}

# Upload
# Directory ./public/ is uploaded to s3
# resource "aws_s3_object" "provision_source_files" {
#   bucket = aws_s3_bucket.waventopbucket.id
#   for_each = fileset("../public/", "**/*.*")
#   key = each.value
#   source = "../public/${each.value}"
#   # content_type = "text/html"
#   content_type = each.value.content_type
# }

# Upload only index.html
resource "aws_s3_object" "object" {
  bucket = aws_s3_bucket.waventopbucket.id
  # for_each = fileset("../public/", "**/*.*")
  key = "index.html"
  source = "../public/index.html"
  content_type = "text/html"
}

# Creating Bucket Policy
resource "aws_s3_bucket_policy" "public_read_access" {
  bucket = aws_s3_bucket.waventopbucket.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject"
        ],
      "Resource": [
        "${aws_s3_bucket.waventopbucket.arn}",
        "${aws_s3_bucket.waventopbucket.arn}/${aws_s3_object.object.key}"
      ]
    }
  ]
}
EOF
}
# aws_s3_bucket.waventopbucket.arn,
#   "${aws_s3_bucket.waventopbucket.arn}/*",

# View URL
output "object_s3_uri" {
  value = "https://${aws_s3_bucket.waventopbucket.id}.s3.${aws_s3_bucket.waventopbucket.region}.amazonaws.com/index.html"
}
