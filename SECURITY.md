# Security

## Verifying what you installed

goldspec ships two artifacts from each release — `goldspec.pyz`, the command, and
`goldspec-<version>-py3-none-any.whl`, the library — listed in one `SHA256SUMS` and covered by one
detached signature, `SHA256SUMS.asc`. The signature is over the **checksums**, so one signature
covers everything a release contains.

The [instructions on the site](https://plumbspec.org/gold/) install the command and check both. By
hand, with the three files downloaded into one directory:

    gpg --keyserver hkps://keys.openpgp.org --recv-keys 208BC1279656FEEA7C2F9A1D830604D51CA7D4FB
    gpg --verify SHA256SUMS.asc SHA256SUMS
    sha256sum --check --ignore-missing SHA256SUMS

- **The checksum** protects against a corrupted download and a mirror that is not the origin. It
  does not protect against the origin being compromised: whoever served a bad artifact served the
  checksums too.
- **The signature** closes that, and only if the public key reaches you by a route that is not the
  host serving the artifact. That is why the key is on a keyserver.
- **The fingerprint still has to reach you from somewhere you trust.** A keyserver hands out any key
  claiming any identity. Compare the fingerprint across at least two of: this file, plumb's
  `SECURITY.md`, the commit signatures in this repository, and the keyserver.

## The signing key

    208B C127 9656 FEEA 7C2F  9A1D 8306 04D5 1CA7 D4FB

The same key signs plumb's releases, and its signing subkey signs the commits and tags in this
repository, so `git log --show-signature` is an independent place to see it. `gpg --verify` reports
the subkey first and the primary last; the primary above is what to pin, because subkeys rotate.

## Supported versions

goldspec is pre-1.0. Only the current minor is maintained, and what the gate accepts may change
between any two releases until 1.0.0 — [CHANGELOG.md](CHANGELOG.md) says what each one asks of you.

| Version | Supported |
|---|---|
| 0.3.x | current |
| 0.2.x | superseded |
| 0.1.x | superseded |

## Dependencies

- **Python 3.9+**, and the standard library. Below 3.11, where the standard library has no TOML
  parser, `goldspec.toml` is read by a copy of `tomli` that ships inside the package
  (`goldspec/_vendor`) rather than being installed beside it, so there is still nothing to resolve.
- **pytest 8+** is declared for the library, because a gate is a test a project runs in its own
  suite. Nothing in goldspec imports it.

## What goldspec does to your files

**It reads; it never writes.** The gate reads the spec directory, its `goldspec.toml`, any
siblings it names, and the test sources that cite the spec. It changes none of them, sends nothing
anywhere, and keeps no state between runs.

## Reporting a vulnerability

Report it at [support.plumbspec.org](https://support.plumbspec.org).
