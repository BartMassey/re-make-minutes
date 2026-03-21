# re-make-minutes: make Rust Embedded Weekly Meeting Minutes discussion
Bart Massey and Claude Code 2026

Script to create weekly
[rust-embedded/wg](https://github.com/rust-embedded/wg)
meeting minutes discussions on GitHub.

## Usage

```
python3 re-make-minutes.py [DATE] [--dry-run]
```

- `DATE` — meeting date as `YYYY-MM-DD`
  (default: next Tuesday)
- `--dry-run` — print title and body without creating
  the discussion

## Requirements

- Python 3.7+
- [`gh`](https://cli.github.com/) authenticated with an
  account that has permission to create discussions in
  `rust-embedded/wg`

## License

Licensed under either of the "Apache License, Version 2.0"
or the "MIT license" at your option. Please see the
`LICENSE` file in this distribution for license terms.
