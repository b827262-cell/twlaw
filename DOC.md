# twlaw DOC

This repository documents a daily Taiwan market data workflow focused on two data sources:

- TAIFEX institutional futures positioning by contract and date
- TWSE T86 listed-stock institutional net buy/sell

## What the workflow produces

The daily run generates three kinds of artifacts:

- `data/raw/`
  - raw TAIFEX HTML responses
  - raw TWSE T86 JSON responses
- `data/processed/`
  - normalized TAIFEX institutional futures CSV
  - normalized TWSE T86 CSV
- `reports/`
  - daily Markdown report

## Expected TAIFEX futures scope

The TAIFEX parser is designed for these contracts:

- 臺股期貨
- 小型臺指期貨
- 微型臺指期貨

The parser must recognize the institutional futures table semantics, not quote or market-price tables.

Required TAIFEX output columns:

- 日期
- 商品名稱
- 身份別
- 交易多方口數
- 交易多方契約金額千元
- 交易空方口數
- 交易空方契約金額千元
- 交易多空淨額口數
- 交易多空淨額契約金額千元
- 未平倉多方口數
- 未平倉多方契約金額千元
- 未平倉空方口數
- 未平倉空方契約金額千元
- 未平倉多空淨額口數
- 未平倉多空淨額契約金額千元

## TWSE T86 scope

The TWSE T86 parser must validate these outputs:

- 外資
- 投信
- 自營商
- 三大法人合計買賣超

## How to run

From the project root:

```bash
make setup
make daily
make date DATE=YYYYMMDD
```

There is also an offline fixture test for the TAIFEX institutional table parser:

```bash
make test-fixture
```

## Error handling

The implementation should fail clearly when:

- the official response is empty
- the expected institutional futures table cannot be found
- required columns are missing
- the TWSE T86 payload does not contain the expected institutional fields

## Known limitations

- Live official site access may be blocked by network or DNS restrictions in sandboxed environments.
- TAIFEX or TWSE page structure changes may require parser updates.
- The parser intentionally rejects quote-style futures tables.
