# Contributing

Thanks for helping improve the benchmark.

## Before opening a pull request

- Keep examples synthetic or provide documented permission and remove identifying details.
- Never include real phone numbers, names, account numbers, UPI IDs, OTPs, payment URLs, or private messages.
- Use reserved `.invalid` domains for illustrative links; do not include live malicious links.
- Have a fluent speaker review each new Hindi or Telugu message for natural wording and meaning.
- Record the example's provenance and the intended category. Avoid copying a message from a person or a private channel.
- Add or update tests when changing evaluation behavior.

## Development

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
bhasha-scam-bench evaluate --json
```

Keep dependencies minimal and explain any proposed runtime dependency in the pull request.
