# Repository instructions

## Public code-field compatibility invariant

- Keep existing public subject parameters named `symbol`, including index,
  sector, ETF, and other subjects already exposed under that name.
- When an endpoint has a second constituent-security parameter, keep it named
  `con_symbol`.
- Do not replace these public fields with `index_code`, `bk_code`, `con_code`,
  `etf_code`, or other type-specific names merely for naming uniformity.
- Internal service or database fields such as `ts_code`, `index_code`, and
  `con_code` do not determine the Python SDK's public parameter names.
- Preserve backward compatibility in README examples, SDK calls, endpoint
  metadata, and tests. A breaking change requires a separately versioned API.
