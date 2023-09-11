import openai
import os
from typing import Optional
import json


class OpenAIClient:
    def __init__(self):
        openai.organization = "org-79wTeMDwJKLtMWOcnQRg6ozv"
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def getImportantHeaders(self, messages):

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            temperature=0,
            messages=messages,
            functions=[
                {
                    "name": "categories_headers",
                    "description": "You will be presented with the start of a file and your job is to find the names of specific columns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "string",
                                "description": "The csv header name of the amount column"
                            },
                            "date": {
                                "type": "string",
                                "description": "The csv header name of the date column"
                            },
                            "description": {
                                "type": "array",
                                "description": "The csv header names that could contribute to a description",
                                "items": {"type": "string"}
                            }
                        }
                    }
                }
            ],
            function_call='auto',
            max_tokens=1024
        )

        return response.choices[0].message.function_call.arguments

    def categorizeTransactions(self, transactions, overrideCategories, custom_rules):
        print(f"categorizeTransactions({len(transactions)})")

        extracted_data = ['t_id, description, recipient, date, amount']

        for data in transactions:
            print(f"data")
            t_id = data.t_id
            description = data.description
            date = data.date
            amount = data.amount
            extracted_data.append(f"{t_id}, {description}, {date}, {amount}")

        content = "\n".join(extracted_data)

        print(
            f"openai.ChatCompletion:content\n({content})")

        if (len(custom_rules) > 0):
            custom_rules_str = f"\nconsider these rules: {custom_rules}"
        else:
            custom_rules_str = ''

        function = {
            "name": "categories_headers",
                    "description": "You job is to categorize a given transactions. Include why you chose that category\n\n" +
            custom_rules_str,
                    "parameters": {
                        "type": 'object',
                        "properties": {
                            "categories": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "t_id": {
                                            "type": "string",
                                            "description": "The t_id of the row being categorised"
                                        },
                                        "category": {
                                            "type": "string",
                                            "enum": overrideCategories,
                                            "description": "The category of this transaction"
                                        },
                                        "category_reason": {
                                            "type": "string",
                                            "description": "Why this transaction is in this category"
                                        }
                                    },
                                    "required": ["t_id", "category", "category_reason"],
                                }
                            }
                        }
                    }
        }

        print(
            f"openai.ChatCompletion:function:\n({json.dumps(function, indent=4)})")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            temperature=0,
            messages=[{
                "role": 'user',
                "content": content,
            }],
            functions=[
                function
            ],
            function_call='auto',
            max_tokens=1024
        )

        result = json.loads(
            response.choices[0].message.function_call.arguments)
        print(
            f"openai.ChatCompletion:function:\n({json.dumps(result, indent=4)})")

        return result
