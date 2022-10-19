Sigstore Ansible GitHub Action
=========================

A first try at a GitHub Action forked from the [sigstore-python GitHub Action](https://github.com/sigstore/gh-action-sigstore-python) to sign Ansible content with Sigstore.

WARNING: This GitHub Action is still at an experimental state.

## Index

* [Usage](#usage)
* [Configuration](#configuration)
* [Licensing](#licensing)
* [Code of Conduct](#code-of-conduct)

## Usage

Add this GitHub Action to one of your workflows:

```yaml
jobs:
  sign-collection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: install
        run: python -m pip install .
      - uses: mayaCostantini/sigstore-ansible-github-action@v0.0.1
        with:
          content-type: collection
```

Your workflow must have permission to request the OIDC token to authenticate with. This can be done
by having a top-level `permission` setting for your workflow.

```yaml
permissions:
  id-token: write
```

More information about permission settings can be found [here](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#adding-permissions-settings).

## Configuration

`sigstore-ansible-github-action` automatically generates and signs a MANIFEST.json file containing the checksums for all the files in the content repository on a pull request merge or new release creation, producing the MANIFEST.json.asc and MANIFEST.json.crt artifacts that will be used for signature verification in Ansible.

### `identity-token`

**Default**: Empty (the GitHub Actions credential will be used)

The `identity-token` setting controls the OpenID Connect token provided to Fulcio. By default, the
workflow will use the credentials found in the GitHub Actions environment.

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    identity-token: ${{ IDENTITY_TOKEN  }} # assigned elsewhere
```

### `oidc-client-id`

**Default**: `sigstore`

The `oidc-client-id` setting controls the OpenID Connect client ID to provide to the OpenID Connect
Server during OAuth2.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    oidc-client-id: alternative-sigstore-id
```

### `oidc-client-secret`

**Default**: Empty (no OpenID Connect client secret provided by default)

The `oidc-client-secret` setting controls the OpenID Connect client secret to provide to the OpenID
Connect Server during OAuth2.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    oidc-client-secret: alternative-sigstore-secret
```

### `signature`

**Default**: Empty (signature files will get named as `{input}.sig`)

The `signature` setting controls the name of the output signature file.
Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    signature: custom-signature-filename.sig
```

### `certificate`

**Default**: Empty (certificate files will get named as `{input}.crt`)

The `certificate` setting controls the name of the output certificate file.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    certificate: custom-certificate-filename.crt
```

### `fulcio-url`

**Default**: `https://fulcio.sigstore.dev`

The `fulcio-url` setting controls the Fulcio instance to retrieve the ephemeral signing certificate
from. This setting cannot be used in combination with the `staging` setting.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    fulcio-url: https://fulcio.sigstage.dev
```

### `rekor-url`

**Default**: `https://rekor.sigstore.dev`

The `rekor-url` setting controls the Rekor instance to upload the file signature to. This setting
cannot be used in combination with the `staging` setting.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    rekor-url: https://rekor.sigstage.dev
```

### `ctfe`

**Default**: `ctfe.pub` (the CTFE key embedded in `sigstore-python`)

The `ctfe` setting is a path to a PEM-encoded public key for the CT log. This setting cannot be used
in combination with the `staging` setting.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    ctfe: ./path/to/ctfe.pub
```

### `rekor-root-pubkey`

**Default**: `rekor.pub` (the Rekor key embedded in `sigstore-python`)

The `rekor-root-pubkey` setting is a path to a PEM-encoded public key for Rekor. This setting cannot
be used in combination with `staging` setting.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    ctfe: ./path/to/rekor.pub
```

### `staging`

**Default**: `false`

The `staging` setting controls whether or not `sigstore-python` uses sigstore's staging instances,
instead of the default production instances.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    staging: true
```

### `verify`

**Default**: `true`

The `verify` setting controls whether or not the generated signatures and certificates are
verified with the `sigstore verify` subcommand after all files have been signed.

This is not strictly necessary but can act as a smoke test to ensure that all signing artifacts were
generated properly and the signature was properly submitted to Rekor.


Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    verify: false
```

### `verify-cert-email`

**Default**: Empty

The `verify-cert-email` setting controls whether to verify the Subject Alternative Name (SAN) of the
signing certificate after signing has taken place. If it is set, `sigstore-python` will compare the
certificate's SAN against the provided value.

This setting only applies if `verify` is set to `true`.

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    verify-cert-email: john.smith@example.com
```

### `verify-oidc-issuer`

**Default**: `https://oauth2.sigstore.dev/auth`

The `verify-oidc-issuer` setting controls whether to verify the issuer extension of the signing
certificate after signing has taken place. If it is set, `sigstore-python` will compare the
certificate's issuer extension against the provided value.

This setting only applies if `verify` is set to `true`.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    verify-oidc-issuer: https://oauth2.sigstage.dev/auth
```

### `upload-signing-artifacts`

**Default**: `false`

The `upload-signing-artifacts` setting controls whether or not `sigstore-python` creates
[workflow artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
for the outputs produced by signing operations.

By default, no workflow artifacts are uploaded. When enabled, the default
workflow artifact retention period is used.

Example:

```yaml
- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    upload-signing-artifacts: true
```

### `release-signing-artifacts`

**Default**: `false`

The `release-signing-artifacts` setting controls whether or not `sigstore-python`
uploads signing artifacts to the release publishing event that triggered this run.

By default, no release assets are uploaded.

Requires the [`contents: write` permission](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token).

Example:

```yaml
permissions:
  contents: write

# ...

- uses: sigstore/gh-action-sigstore-python@v0.0.9
  with:
    release-signing-artifacts: true
```

## Licensing

`gh-action-sigstore-python` is licensed under the Apache 2.0 License.

## Code of Conduct

Everyone interacting with this project is expected to follow the
[sigstore Code of Conduct](https://github.com/sigstore/.github/blob/main/CODE_OF_CONDUCT.md)

## Security

Should you discover any security issues, please refer to sigstore's [security
process](https://github.com/sigstore/.github/blob/main/SECURITY.md).

## Info

`gh-action-sigstore-python` is developed as part of the [`sigstore`](https://sigstore.dev) project.

We also use a [slack channel](https://sigstore.slack.com)!
Click [here](https://join.slack.com/t/sigstore/shared_invite/zt-mhs55zh0-XmY3bcfWn4XEyMqUUutbUQ) for the invite link.
