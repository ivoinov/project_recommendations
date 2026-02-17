# CSV Specification (Multi-Shop Ingestion)

## Overview
This specification defines the required CSV schema and validation rules for multi-shop product and order ingestion. Validation is a dry-run only, with error summaries reported per file and per shop. All validation rules are applied after normalization.

## File Naming
- Products: `{shop_id}_products.csv`
- Orders: `{shop_id}_orders.csv`

`shop_id` is a lowercase slug (example: `acme_products.csv`). Products and orders are both required for a complete shop validation run.

## Encoding and Delimiter
- Encoding: UTF-8
- Delimiter: semicolon (`;`)
- Header row: required

## Merge / Append Behavior
Multiple files per shop per day are supported. Files are processed in lexical order and rows are appended in sequence.

- Products: if the same `sku` appears multiple times across files, the last occurrence wins.
- Orders: multiple rows per order are allowed (one row per line item). If the same `order_id` + `sku` appears multiple times, the last occurrence wins.

## CSV Schema

### Products (Required Fields)
- `sku`
- `name`
- `category`
- `price`
- `in_stock`
- `short_description`
- `meta_title`
- `meta_description`

### Products (Optional Fields)
- `description`
- `image_url`
- `brand`
- `tags`
- `meta_keywords`

### Orders (Required Fields)
Each row represents a single line item in an order.

- `order_id`
- `shop_id`
- `customer_id`
- `order_date`
- `sku`
- `qty`
- `price`

### Orders (Optional Fields)
- `status`
- `currency`
- `total`

## Normalization Rules (Applied Before Validation)
- Trim whitespace on all string fields.
- Normalize `in_stock` to a boolean (`true/false`, `1/0`, `yes/no` are accepted).
- Convert `price` and `qty` to decimal values.
- Parse `order_date` to an ISO-8601 date string (`YYYY-MM-DD`).
- Keep `category` as-is (no mapping); only trimming applies.

## Validation Rules
- Missing required fields: record an error for the row and skip it.
- Type errors: record an error if decimal or date parsing fails.
- Validation operates on normalized values, and normalized rows are returned to callers for downstream ingestion.

## Error Threshold
- Error threshold: **5%** of total rows per shop.
- A shop fails validation if its error rate exceeds the threshold.

## Output Expectations
Validation reports:
- Per-file totals and error counts
- Per-shop totals, error counts, and error rate
- Normalized rows for downstream ingestion (no DB writes)
