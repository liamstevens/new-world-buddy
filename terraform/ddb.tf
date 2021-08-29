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

