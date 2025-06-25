import os
import json
import logging
import asyncio
from typing import List, Optional, Dict, Any

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

from .summarizer import SummarizerConfig

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

class PlanAnalysisAgent:
    """
    Agentic workflow to analyze Terraform plan changes with Azure context.
    This agent first retrieves Azure information via function calling,
    then performs impact and risk analysis of the plan.
    """
    def __init__(self, ai_config: Dict[str, Any], azure_config: Dict[str, Any]):
        # Wrap ai_config dict into SummarizerConfig
        if isinstance(ai_config, SummarizerConfig):
            self.config = ai_config
        else:
            self.config = SummarizerConfig(
                provider=ai_config.get('provider', ''),
                model=ai_config.get('model', ''),
                api_key=ai_config.get('api_key', ''),
                max_tokens=ai_config.get('max_tokens', 2048),
                temperature=ai_config.get('temperature', 0.1),
                system_prompt=ai_config.get('system_prompt'),
                timeout=ai_config.get('timeout', 60)
            )
        if AsyncOpenAI is None:
            raise ImportError("OpenAI package is not installed")
        self.client = AsyncOpenAI(api_key=self.config.api_key)
        self.azure_config = azure_config
        self.logger = logging.getLogger(__name__)

    async def fetch_azure_info(
        self,
        subscription_id: str,
        filter_resource_groups: Optional[List[str]] = None,
        include_resources: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve Azure resource groups and resources from a subscription.
        """
        credential = DefaultAzureCredential()
        client = ResourceManagementClient(credential, subscription_id)
        # Fetch resource groups
        rg_list = client.resource_groups.list()
        rgs = []
        for rg in rg_list:
            if not filter_resource_groups or rg.name in filter_resource_groups:
                rgs.append(rg.as_dict())
        info: Dict[str, Any] = {"resource_groups": rgs}
        # Optionally fetch resources
        if include_resources:
            res_list = client.resources.list()
            resources = []
            for res in res_list:
                # resource id path: /subscriptions/.../resourceGroups/{rg}/...
                parts = res.id.split('/')
                rg_name = parts[4] if len(parts) > 4 else None
                if not filter_resource_groups or rg_name in filter_resource_groups:
                    resources.append(res.as_dict())
            info["resources"] = resources
        return info

    async def run(self, plan_changes: List[Dict[str, Any]]) -> str:
        """
        Execute the agent workflow:
        1. Fetch Azure info via function calling
        2. Perform analysis combining plan changes and Azure info
        Returns final analysis as a markdown string.
        """
        # Prepare plan content
        plan_json = json.dumps({"changes": plan_changes}, default=str)
        # Azure parameters
        sub_id = self.azure_config.get("subscription_id") or os.getenv("AZURE_SUBSCRIPTION_ID")
        filter_rgs = self.azure_config.get("filter_resource_groups") or []
        include_res = self.azure_config.get("include_resources", False)
        # Define function spec for Azure info
        functions = [{
            "name": "fetch_azure_info",
            "description": "Retrieve Azure resource group and resource info",
            "parameters": {
                "type": "object",
                "properties": {
                    "subscription_id": {"type": "string"},
                    "filter_resource_groups": {"type": "array", "items": {"type": "string"}},
                    "include_resources": {"type": "boolean"}
                },
                "required": ["subscription_id"]
            }
        }]
        # Initial messages
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": (
                "You are an expert Terraform and Azure analyst. "
                "First, call the function 'fetch_azure_info' to retrieve Azure subscription information."
            )},
            {"role": "user", "content": f"Terraform plan changes:\n{plan_json}"}
        ]
        # First API call to fetch Azure info
        resp = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            functions=functions,
            function_call="auto",
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        msg = resp.choices[0].message
        if msg.get("function_call"):
            fn_name = msg["function_call"]["name"]
            args = json.loads(msg["function_call"]["arguments"] or "{}")
            # Ensure args include necessary config
            args.setdefault("subscription_id", sub_id)
            args.setdefault("filter_resource_groups", filter_rgs)
            args.setdefault("include_resources", include_res)
            # Execute function locally
            azure_info = await self.fetch_azure_info(**args)
            # Append function response and continue
            messages.append(msg)
            messages.append({"role": "function", "name": fn_name, "content": json.dumps(azure_info, default=str)})
            # Second API call for combined analysis
            analysis_resp = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return analysis_resp.choices[0].message.content
        # If no function call, assume content is analysis
        return msg.get("content", "")