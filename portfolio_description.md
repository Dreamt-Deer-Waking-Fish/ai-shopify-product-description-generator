# Upwork Case Study: Shopify Product Copy Generator

## Portfolio Title

I built a Python tool that turns product CSV rows into Shopify-ready titles, descriptions, feature bullets, and SEO metadata.

## Client Scenario

An ecommerce seller has product data in a spreadsheet, but the listing copy is incomplete or inconsistent. The seller needs better product descriptions and SEO fields before importing products into Shopify or another ecommerce platform.

## My Solution

I created a Python workflow that reads product attributes from CSV and generates enhanced product copy into a new spreadsheet. The project includes a mock mode for demos without credentials and an optional OpenAI mode for API-backed generation.

## Key Deliverables

- Product CSV reader
- Mock generation mode for public demos
- Optional OpenAI generation mode
- Enhanced CSV export
- Generated titles, descriptions, bullet points, and SEO meta descriptions
- Safe `.env.example` setup
- README with setup, usage, validation, and customization notes

## Business Result

This workflow helps ecommerce teams create consistent first-draft product copy faster. A human can review and edit the output before publishing, while the repetitive drafting work is automated.

## Technologies Used

Python, pandas, python-dotenv, OpenAI SDK, CSV export workflow.

## How I Would Customize It for a Client

For a real store, I would add brand voice rules, category-specific prompts, Shopify import column mapping, language options, and review status fields for the content team.
