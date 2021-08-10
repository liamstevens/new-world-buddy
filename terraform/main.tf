#DynamoDB

resource "aws_dynamodb_table" "recipe_table" {
    name = "CraftingRecipes"
    billing_mode = "PROVISIONED"
    read_capacity = 25
    write_capacity = 25
    hash_key = "tradeskill"
    range_key = "recipelevel"

    attribute {
      name = "tradeskill"
      type = "S"
    }

    attribute {
      name = "recipelevel"
      type = "N"
    }

    attribute {
      name = "ingredients"
      type = "S"
    }

    ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }
  tags = {
    Name        = "CraftingRecipes"
    Environment = "production"
  }
}