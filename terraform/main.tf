terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "feedback-engineering"

    workspaces {
      name = "new-world-buddy"
    }
  }
}

provider "aws" {
  region = "ap-southeast-2"
}

#DynamoDB

resource "aws_dynamodb_table" "recipe_table" {
    name = "CraftingRecipes"
    billing_mode = "PROVISIONED"
    read_capacity = 25
    write_capacity = 25
    hash_key = "tradeskill"
    range_key = "name"

    attribute {
      name = "tradeskill"
      type = "S"
    }

    /*attribute {
      name = "recipelevel"
      type = "N"
    }*/

    attribute {
      name = "name"
      type = "S"
    }
/*
    attribute {
      name = "ingredients"
      type = "B"
    }
*/
    ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }
  tags = {
    Name        = "CraftingRecipes"
    Environment = "production"
  }
}