from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Dict, List

import pandas as pd
from dotenv import load_dotenv


OUTPUT_COLUMNS = [
    "sku",
    "original_title",
    "improved_title",
    "product_description",
    "bullet_point_features",
    "seo_meta_description",
]


def configure_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(output_dir / "run.log", mode="w", encoding="utf-8"),
        ],
    )


def load_products(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Product file not found: {input_path}")
    products = pd.read_csv(input_path)
    required = ["sku", "title", "category", "material", "features", "target_customer"]
    missing = [column for column in required if column not in products.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    products = products.fillna("")
    logging.info("Loaded %s products from %s", len(products), input_path)
    return products


def mock_generate(row: pd.Series) -> Dict[str, str]:
    title = str(row["title"]).strip()
    category = str(row["category"]).strip()
    material = str(row["material"]).strip()
    features = [item.strip() for item in str(row["features"]).split(";") if item.strip()]
    audience = str(row["target_customer"]).strip() or "everyday shoppers"

    improved_title = f"{title} - {material} {category} for {audience}".replace("  ", " ").strip()
    feature_sentence = ", ".join(features[:3]) if features else "practical design, dependable quality, everyday comfort"
    description = (
        f"Upgrade your routine with {title}, a {category.lower()} designed for {audience}. "
        f"Made with {material.lower()}, this product focuses on {feature_sentence}. "
        "It is easy to position in a Shopify catalog and clear enough for customers to understand the value quickly."
    )
    bullets = "\n".join(f"- {feature}" for feature in (features or ["Reliable everyday design", "Easy to merchandise", "Clear customer value"]))
    seo = f"Shop {title}, a {material.lower()} {category.lower()} with {feature_sentence} for {audience}."
    return {
        "improved_title": improved_title[:120],
        "product_description": description,
        "bullet_point_features": bullets,
        "seo_meta_description": seo[:155],
    }


def openai_generate(row: pd.Series, model: str) -> Dict[str, str]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError("OpenAI package is not installed. Run: pip install openai") from exc

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = {
        "sku": row["sku"],
        "title": row["title"],
        "category": row["category"],
        "material": row["material"],
        "features": row["features"],
        "target_customer": row["target_customer"],
    }
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You write concise Shopify product copy. Return only valid JSON with keys "
                    "improved_title, product_description, bullet_point_features, seo_meta_description."
                ),
            },
            {"role": "user", "content": json.dumps(prompt)},
        ],
        temperature=0.6,
    )
    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)
    return {
        "improved_title": str(parsed.get("improved_title", "")).strip()[:120],
        "product_description": str(parsed.get("product_description", "")).strip(),
        "bullet_point_features": str(parsed.get("bullet_point_features", "")).strip(),
        "seo_meta_description": str(parsed.get("seo_meta_description", "")).strip()[:155],
    }


def choose_mode(requested_mode: str) -> str:
    if requested_mode == "mock":
        return "mock"
    if requested_mode == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is required for --mode openai")
        return "openai"
    return "openai" if os.getenv("OPENAI_API_KEY") else "mock"


def enhance_products(products: pd.DataFrame, mode: str, model: str) -> pd.DataFrame:
    rows: List[Dict[str, str]] = []
    for _, product in products.iterrows():
        generated = openai_generate(product, model) if mode == "openai" else mock_generate(product)
        rows.append(
            {
                "sku": str(product["sku"]),
                "original_title": str(product["title"]),
                **generated,
            }
        )
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def export_products(products: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    products.to_csv(output_path, index=False, encoding="utf-8")
    logging.info("Enhanced product CSV saved to %s", output_path)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Shopify product titles, descriptions, bullets, and SEO metadata.")
    parser.add_argument("--input", default="sample_data/products.csv", help="Input products CSV.")
    parser.add_argument("--output", default="output/enhanced_products.csv", help="Enhanced products CSV output path.")
    parser.add_argument("--mode", choices=["auto", "mock", "openai"], default="auto", help="Generation mode.")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model used when OPENAI_API_KEY is available.")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    output_path = Path(args.output)
    configure_logging(output_path.parent)

    try:
        mode = choose_mode(args.mode)
        logging.info("Using generation mode: %s", mode)
        products = load_products(Path(args.input))
        enhanced = enhance_products(products, mode, args.model)
        export_products(enhanced, output_path)
        logging.info("Done. Enhanced %s products.", len(enhanced))
    except Exception as exc:
        logging.exception("Product copy generation failed: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
