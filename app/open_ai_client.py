import openai
import os
from typing import Optional


class OpenAIClient:
    def __init__(self, organization: str):
        openai.organization = organization
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

    def categorizeTransactions(self, transactions, overrideCategories):

        if not overrideCategories:
            overrideCategories = [
                'Housing',
                'Groceries',
                'Eating Out',
                'Transportation',
                'Healthcare',
                'Entertainment',
                'Apparel',
                'Income',
                'Debts'
            ]

        extracted_data = []

        for data in transactions:
            t_id = data[0]
            description = data[4]
            date = data[3]
            amount = data[5]
            extracted_data.append(f"{t_id}, {description}, {date}, {amount}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            temperature=0,
            messages=[{
                "role": 'user',
                "content": "\n".join(extracted_data),
            }],
            functions=[
                {
                    "name": "categories_headers",
                    "description": "You job is to categorize a given transaction based on the following categories:" + "\n".join(overrideCategories),
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
                                    },
                                    "required": ["ts_id", "category"],
                                }
                            }
                        }
                    }
                }
            ],
            function_call='auto',
            max_tokens=1024
        )

        return response.choices[0].message.function_call.arguments
