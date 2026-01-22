# Dependencies Explanation

## Why So Many Packages?

When you install `langflow`, it pulls in **~500+ packages**. This is expected and normal because:

1. **Langflow is a full-featured framework** that includes:
   - LLM provider integrations (OpenAI, Anthropic, Google, etc.)
   - Vector database clients (ChromaDB, Pinecone, Qdrant, etc.)
   - Langchain integrations
   - Data processing libraries (pandas, numpy, etc.)
   - Many other optional features

2. **Our components only need:**
   - `langflow` - For the Component framework and UI
   - `boto3` - For AWS SDK operations
   - `pydantic` - For data validation/models
   - `jinja2` - Optional, for Terraform generation

## What We Actually Use

Our components import:
- `lfx.custom.custom_component.component.Component` - Component base class
- `lfx.io.*` - Input/Output types (StrInput, DataInput, etc.)
- `lfx.schema.Data` - Data schema
- `boto3` - AWS SDK
- `pydantic` - Data models

## Minimal Installation (Not Recommended)

If you want to test components without the full UI, you could try:
```bash
pip install lfx langflow-base boto3 pydantic
```

However, this won't give you the Langflow UI server. For the full experience, use `requirements.txt`.

## Summary

- **500+ packages is normal** for Langflow
- **We only directly use 4 packages** (langflow, boto3, pydantic, jinja2)
- **The rest are Langflow's optional dependencies**
- **This is expected behavior** - Langflow is designed as a comprehensive framework
