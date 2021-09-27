resource "aws_s3_bucket" "lambda_storage" {
  bucket        = "barcode-lambda-bucket"
  acl           = "private"
  force_destroy = true
}

data "archive_file" "lambda_crafting" {
  type        = "zip"
  source_dir  = "./lambda/crafting"
  output_path = "./lambda/crafting.zip"
}

data "archive_file" "lambda_signup" {
  type        = "zip"
  source_dir  = "./lambda/signup"
  output_path = "./lambda/signup.zip"
}

data "archive_file" "lambda_getroster" {
  type        = "zip"
  source_dir  = "./lambda/getroster"
  output_path = "./lambda/getroster.zip"
}
resource "aws_s3_bucket_object" "lambda_crafting" {
  bucket = aws_s3_bucket.lambda_storage.id

  key    = "crafting.zip"
  source = data.archive_file.lambda_crafting.output_path

  etag = filemd5(data.archive_file.lambda_crafting.output_path)
}

resource "aws_s3_bucket_object" "lambda_signup" {
  bucket = aws_s3_bucket.lambda_storage.id

  key    = "signup.zip"
  source = data.archive_file.lambda_signup.output_path

  etag = filemd5(data.archive_file.lambda_signup.output_path)
}

resource "aws_s3_bucket_object" "lambda_getroster" {
  bucket = aws_s3_bucket.lambda_storage.id

  key    = "getroster.zip"
  source = data.archive_file.lambda_getroster.output_path

  etag = filemd5(data.archive_file.lambda_getroster.output_path)
}


resource "aws_lambda_function" "crafting" {
  function_name = "CraftingCalculator"

  s3_bucket        = aws_s3_bucket.lambda_storage.id
  s3_key           = aws_s3_bucket_object.lambda_crafting.key
  runtime          = "python3.7"
  handler          = "craft-path.lambda_handler"
  source_code_hash = data.archive_file.lambda_crafting.output_base64sha256
  role             = aws_iam_role.lambda_exec.arn
  timeout          = "120"
  memory_size      = "256"
}

resource "aws_lambda_function" "signup" {
  function_name = "WarSignup"

  s3_bucket        = aws_s3_bucket.lambda_storage.id
  s3_key           = aws_s3_bucket_object.lambda_signup.key
  runtime          = "python3.7"
  handler          = "signup-war.lambda_handler"
  source_code_hash = data.archive_file.lambda_signup.output_base64sha256
  role             = aws_iam_role.signup_lambda_exec.arn
  timeout          = "120"
  memory_size      = "128"
}

resource "aws_lambda_function" "getroster" {
  function_name = "GetRoster"

  s3_bucket        = aws_s3_bucket.lambda_storage.id
  s3_key           = aws_s3_bucket_object.lambda_getroster.key
  runtime          = "python3.7"
  handler          = "get-roster.lambda_handler"
  source_code_hash = data.archive_file.lambda_getroster.output_base64sha256
  role             = aws_iam_role.lambda_exec.arn
  timeout          = "120"
  memory_size      = "128"
}

resource "aws_cloudwatch_log_group" "crafting" {
  name              = "/aws/lambda/${aws_lambda_function.crafting.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "signup" {
  name              = "/aws/lambda/${aws_lambda_function.signup.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "getroster" {
  name              = "/aws/lambda/${aws_lambda_function.getroster.function_name}"
  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role" "signup_lambda_exec" {
  name = "serverless_lambda_ddb_edit"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_ddb_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "signup_ddb_policy" {
  role       = aws_iam_role.signup_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}