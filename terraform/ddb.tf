#DynamoDB

resource "aws_dynamodb_table" "recipe_table" {
  name         = "CraftingRecipes"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "tradeskill"
  range_key    = "name"

  attribute {
    name = "tradeskill"
    type = "S"
  }

  attribute {
    name = "name"
    type = "S"
  }

  tags = {
    Name        = "CraftingRecipes"
    Environment = "production"
  }
}

resource "aws_dynamodb_table" "recipe_table" {
  name         = "WarRoster"
  billing_mode = "PROVISIONED"
  read_capacity  = 25
  write_capacity = 25
  hash_key     = "username"
  range_key    = "level"

  attribute {
    name = "username"
    type = "S"
  }

  attribute {
    name = "level"
    type = "N"
  }

  tags = {
    Name        = "WarRoster"
    Environment = "production"
  }
}
