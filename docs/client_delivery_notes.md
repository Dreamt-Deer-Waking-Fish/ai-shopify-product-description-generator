# Client Delivery Notes

## What the Client Receives

- A reusable Python script for bulk product copy generation
- Sample product CSV showing the required input format
- Enhanced CSV output with generated ecommerce fields
- Mock mode for testing without credentials
- Optional OpenAI mode for production-style generation
- Documentation for setup, usage, and credential safety

## Acceptance Checklist

- `python -m py_compile main.py` passes
- `python main.py --mode mock` exports `output/enhanced_products.csv`
- Output contains title, description, feature bullet, and SEO fields
- `.env.example` is included
- `.env` and real API keys are excluded from Git

## Client Customization Options

- Add brand voice settings
- Add product category-specific prompts
- Add Shopify import column names
- Add multilingual generation
- Add review status and approval columns
- Add image alt text generation
