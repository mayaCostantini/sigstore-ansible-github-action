Ansible-sign GitHub Action
=========================

⚠️ This project is a work in progress and is not ready for production use.

[![CI](https://github.com/mayaCostantini/sigstore-ansible-github-action/actions/workflows/ci.yml/badge.svg)](https://github.com/mayaCostantini/sigstore-ansible-github-action/actions/workflows/ci.yml)
[![Self-test](https://github.com/mayaCostantini/sigstore-ansible-github-action/actions/workflows/selftest.yml/badge.svg)](https://github.com/mayaCostantini/sigstore-ansible-github-action/actions/workflows/selftest.yml)

A GitHub Action that uses [`ansible-sign`](https://github.com/ansible/ansible-sign) to generate Sigstore signatures for Ansible projects.
This repository is a fork of [`gh-action-sigstore-python`](https://github.com/sigstore/gh-action-sigstore-python), which uses [`sigstore-python`](https://github.com/sigstore/sigstore-python) to sign repository artifacts. For more information on project Sigstore, see the official [website](https://sigstore.dev/) and [documentation](https://docs.sigstore.dev/).

As an Ansible project developer, you can use this GitHub Action to automatically sign your project on a new commit or release.
The `ansible-sign` verification materials for the project is generated under a new `.ansible-sign` directory and contains:


## Index

* [Usage](#usage)
* [Configuration](#configuration)
  * [⚠️ Internal options ⚠️](#internal-options)
* [Info](#info)

## Usage

Add `mayaCostantini/sigstore-ansible-github-action` to one of your workflows:

```yaml
jobs:
  sign-project:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write
    steps:
      - uses: actions/checkout@v3
      - name: install
        run: python -m pip install .
      - uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
```

Note: Your workflow **must** have permission to request the OIDC token to authenticate with,
and the `contents: write` permission for the Action to commit signature artifacts in the repository.
This can be done by setting `id-token: write` on your job (as above) or workflow.

More information about permission settings can be found
[here](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#adding-permissions-settings).

## Configuration

`sigstore-ansible-github-action` takes a variety of configuration inputs, most of which are
optional.

### `project-path`

The `project-path` input is optional and defaults to the root of the current repository.

Sign a repository sub-path:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    inputs:
      project-path: ./somesubpath/
```

### `identity-token`

**Default**: Empty (the GitHub Actions credential will be used)

The `identity-token` setting controls the OpenID Connect token provided to Fulcio. By default, the
workflow will use the credentials found in the GitHub Actions environment.

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    identity-token: ${{ IDENTITY_TOKEN  }} # assigned elsewhere
```

### `oidc-client-id`

**Default**: `sigstore`

The `oidc-client-id` setting controls the OpenID Connect client ID to provide to the OpenID Connect
Server during OAuth2.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    oidc-client-id: alternative-sigstore-id
```

### `oidc-client-secret`

**Default**: Empty (no OpenID Connect client secret provided by default)

The `oidc-client-secret` setting controls the OpenID Connect client secret to provide to the OpenID
Connect Server during OAuth2.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
    oidc-client-secret: alternative-sigstore-secret
```

### `fulcio-url`

**Default**: `https://fulcio.sigstore.dev`

The `fulcio-url` setting controls the Fulcio instance to retrieve the ephemeral signing certificate
from. This setting cannot be used in combination with the `staging` setting.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    fulcio-url: https://fulcio.sigstage.dev
```

### `rekor-url`

**Default**: `https://rekor.sigstore.dev`

The `rekor-url` setting controls the Rekor instance to upload the file signature to. This setting
cannot be used in combination with the `staging` setting.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    rekor-url: https://rekor.sigstage.dev
```

### `ctfe`

**Default**: `ctfe.pub` (the CTFE key embedded in `sigstore-python`)

The `ctfe` setting is a path to a PEM-encoded public key for the CT log. This setting cannot be used
in combination with the `staging` setting.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    ctfe: ./path/to/ctfe.pub
```

### `rekor-root-pubkey`

**Default**: `rekor.pub` (the Rekor key embedded in `sigstore-python`)

The `rekor-root-pubkey` setting is a path to a PEM-encoded public key for Rekor. This setting cannot
be used in combination with `staging` setting.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    ctfe: ./path/to/rekor.pub
```

### `staging`

**Default**: `false`

The `staging` setting controls whether or not `sigstore-python` uses sigstore's staging instances,
instead of the default production instances.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    staging: true
```

### `verify`

**Default**: `false`

The `verify` setting controls whether or not the generated signatures and certificates are
verified with the `ansible-sign project sigstore-verify` subcommand after the project has been signed.

This is **not strictly necessary** but can act as a smoke test to ensure that all
signing artifacts were generated properly and the signature was properly
submitted to Rekor.

If `verify` is enabled, then you **must** also pass the `verify-cert-identity`
and `verify-oidc-issuer` settings. Failing to pass these will produce an error.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    verify: true
    verify-oidc-issuer: https://some-oidc-issuer.example.com
    verify-cert-identity: some-identity
```

### `verify-cert-identity`

**Default**: Empty

The `verify-cert-identity` setting controls whether to verify the Subject Alternative Name (SAN) of the
signing certificate after signing has taken place. If it is set, `ansible-sign` will compare the
certificate's SAN against the provided value.

This setting only applies if `verify` is set to `true`. Supplying it without `verify: true`
will produce an error.

This setting may only be used in conjunction with `verify-oidc-issuer`.
Supplying it without `verify-oidc-issuer` will produce an error.

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    verify: true
    verify-cert-identity: john.hancock@example.com
    verify-oidc-issuer: https://oauth2.sigstage.dev/auth
```

### `verify-oidc-issuer`

**Default**: `https://oauth2.sigstore.dev/auth`

The `verify-oidc-issuer` setting controls whether to verify the issuer extension of the signing
certificate after signing has taken place. If it is set, `ansible-sign` will compare the
certificate's issuer extension against the provided value.

This setting only applies if `verify` is set to `true`. Supplying it without `verify: true`
will produce an error.

This setting may only be used in conjunction with `verify-cert-identity`.
Supplying it without `verify-cert-identity` will produce an error.

Example:

```yaml
- uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
  with:
    verify: true
    verify-cert-identity: john.hancock@example.com
    verify-oidc-issuer: https://oauth2.sigstage.dev/auth
```

### Internal options
<details>
  <summary>⚠️ Internal options ⚠️</summary>

  Everything below is considered "internal," which means that it
  isn't part of the stable public settings and may be removed or changed at
  any points. **You probably do not need these settings.**

  All internal options are prefixed with `internal-be-careful-`.

  #### `internal-be-careful-debug`

  **Default**: `false`

  The `internal-be-careful-debug` setting enables additional debug logs,
  both within `ansible-sign` itself and the action's harness code. You can
  use it to debug troublesome configurations.

  Example:

  ```yaml
  - uses: mayaCostantini/sigstore-ansible-github-action@v0.0.3
    with:
      internal-be-careful-debug: true
  ```

</details>

## Info

For bug reports, feature requests or enhancement proposals, open an issue in the [`sigstore-ansible-github-action`](https://github.com/mayaCostantini/sigstore-ansible-github-action/issues) repository.

Contact: [mcostant@redhat.com](mcostant@redhat.com).
