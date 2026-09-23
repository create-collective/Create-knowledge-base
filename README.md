# Create knowledge base

An open knowledge base for the **Naya Create** split keyboard and its modules (Tune, Touch, Track)
and dongle: hardware, USB and Bluetooth connectivity, the wire protocol, firmware images and
flashing, storage, recovery, and the NayaFlow / NayaCore host software.

Naya B.V. has ceased operations and no longer supports the Create. Everything here is community
research, built from measurements on real boards, static analysis of the vendor's released software,
and public records such as the FCC and ISED filings. Every fact carries its evidence and a tag
(measured, static, documented, inferred, or reported by a third party), and every open question is
listed with what would settle it.

## Read it

The site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/):

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # Windows
# .venv/bin/python -m pip install -r requirements.txt        # macOS / Linux
.venv/Scripts/python -m mkdocs serve                          # http://127.0.0.1:8000
```

Or read the Markdown under [`docs/`](docs/).

## License

- Pages (`docs/` prose, tables and images): [CC BY 4.0](LICENSE).
- Code snippets and recipes: [MIT](LICENSE-CODE).

Naya Create, Tune, Touch, Track and NayaFlow are Naya's products and names; this project is
independent of Naya and not endorsed by it.
