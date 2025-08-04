resource "aws_bedrockagent_agent" "cs_bot_agent" {
  agent_name              = "cs-bot-agent"
  description             = "Customer service bot agent for shoe purchase support"
  instruction             = file("code/domain/models/agent_tool/support_command.txt")
  foundation_model        = "amazon.nova-lite-v1:0"
  agent_resource_role_arn = aws_iam_role.cs_bot_agent_role.arn
}

resource "aws_iam_role" "cs_bot_agent_role" {
  name = "cs-bot-agent-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "bedrock.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "cs_bot_agent_policy" {
  name = "cs-bot-agentModelPolicy"
  role = aws_iam_role.cs_bot_agent_role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "bedrock:InvokeModel"
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}


resource "aws_bedrockagent_agent_action_group" "cs_bot_action_group" {
  agent_id          = aws_bedrockagent_agent.cs_bot_agent.id
  action_group_name = "cs_bot_action_group"
  agent_version     = "DRAFT"
  action_group_executor {
    lambda = module.llm_lambda.function_arn
  }
  api_schema {
    payload = file("code/domain/models/agent_tool/customerservicebot.json")
  }
}
