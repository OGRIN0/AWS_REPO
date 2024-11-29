data "aws_caller_identity" "current_main" {}
data "aws_partition" "current_main" {}
data "aws_region" "current_main" {}

data "aws_iam_policy_document" "agent_trust_main" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["bedrock.amazonaws.com"]
      type        = "Service"
    }
    condition {
      test     = "StringEquals"
      values   = [data.aws_caller_identity.current_main.account_id]
      variable = "aws:SourceAccount"
    }
    condition {
      test     = "ArnLike"
      values   = ["arn:${data.aws_partition.current_main.partition}:bedrock:${data.aws_region.current_main.name}:${data.aws_caller_identity.current_main.account_id}:agent/*"]
      variable = "aws:SourceArn"
    }
  }
}

data "aws_iam_policy_document" "example_agent_permissions_main" {
  statement {
    actions = ["bedrock:InvokeModel"]
    resources = [
      "arn:${data.aws_partition.current_main.partition}:bedrock:${data.aws_region.current_main.name}::foundation-model/anthropic.claude-v2",
    ]
  }
}

resource "aws_iam_role" "example_main" {
  assume_role_policy = data.aws_iam_policy_document.agent_trust_main.json
  name_prefix        = "AmazonBedrockExecutionRoleForAgents_"
}

resource "aws_iam_role_policy" "example_main" {
  policy = data.aws_iam_policy_document.example_agent_permissions_main.json
  role   = aws_iam_role.example_main.id
}

resource "aws_iam_role" "lambda_role_main" {
  name_prefix        = "lambda-role-action-group-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy_main" {
  role   = aws_iam_role.lambda_role_main.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:::*"
      },
      {
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = "*"
      }
    ]
  })
}

data "archive_file" "lambda_zip_main" {
  type        = "zip"
  source_file = "lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "create_action_group_main" {
  function_name = "CreateActionGroupFunction"
  role          = aws_iam_role.lambda_role_main.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  filename      = data.archive_file.lambda_zip_main.output_path

  environment {
    variables = {
      AGENT_NAME = "my-agent-name-69798999"
    }
  }
}

resource "null_resource" "bedrock_agent_creation_main" {
  provisioner "local-exec" {
    command = join(" ", [
      "aws bedrock-agent create-agent",
      "--agent-name my-agent-name-69798999",
      "--agent-resource-role-arn", 
      aws_iam_role.example_main.arn,
      "--idle-session-ttl-in-seconds 500",
      "--foundation-model anthropic.claude-v2"
    ])
  }

  depends_on = [aws_iam_role.example_main]
}

resource "null_resource" "invoke_lambda_action_group_main" {
  provisioner "local-exec" {
    command = join(" ", [
      "aws lambda invoke",
      "--function-name", aws_lambda_function.create_action_group_main.function_name,
      "--payload '{}'",
      "response.json"
    ])
  }

  depends_on = [aws_lambda_function.create_action_group_main]
}

output "agent_creation_status_main" {
  value = "Bedrock Agent and Action Group created successfully."
}
