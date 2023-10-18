#!/usr/bin/env python3

# Copyright 2022 The Sigstore Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# action.py: run ansible-sign
#
# most state is passed in as environment variables; the only argument
# is the path of the project to sign, by default the root repository path "."

import os
import string
import subprocess
import sys
from pathlib import Path


_HERE = Path(__file__).parent.resolve()
_TEMPLATES = _HERE / "templates"

_summary_path = os.getenv("GITHUB_STEP_SUMMARY")
assert _summary_path is not None
_SUMMARY = Path(_summary_path).open("a")

_RENDER_SUMMARY = os.getenv("GHA_SIGSTORE_PYTHON_SUMMARY", "true") == "true"
_DEBUG = os.getenv("GHA_SIGSTORE_PYTHON_INTERNAL_BE_CAREFUL_DEBUG", "false") != "false"


def _template(name):
    path = _TEMPLATES / f"{name}.md"
    return string.Template(path.read_text())


def _summary(msg):
    if _RENDER_SUMMARY:
        print(msg, file=_SUMMARY)


def _debug(msg):
    if _DEBUG:
        print(f"\033[93mDEBUG: {msg}\033[0m", file=sys.stderr)


def _log(msg):
    print(msg, file=sys.stderr)


def _ansible_sign_sigstore(global_args, sign_args):
    return ["ansible-sign", "project", "sigstore-sign", *global_args, *sign_args]


def _ansible_verify_sigstore(global_args, verify_args):
    return [
        "ansible-sign",
        "project",
        "sigstore-verify",
        "identity",
        *global_args,
        *verify_args,
    ]


def _warning(msg):
    print(f"::warning::⚠️ {msg}")


def _fatal_help(msg):
    print(f"::error::❌ {msg}")
    sys.exit(1)


project_path = sys.argv[1]

# The arguments we pass into `ansible-sign project sigstore-*`
# subcommands get built up in these lists.
sigstore_global_args = []
# Signatures are systematically overwritten
sigstore_sign_args = ["--overwrite"]
sigstore_verify_args = []

# The environment variables that we apply to `ansible-sign project sigstore-*.
sigstore_python_env = {}

# Flag to check whether we want enable the verify step.
enable_verify = bool(os.getenv("GHA_SIGSTORE_PYTHON_VERIFY", "false").lower() == "true")

if _DEBUG:
    sigstore_python_env["SIGSTORE_LOGLEVEL"] = "DEBUG"

identity_token = os.getenv("GHA_SIGSTORE_PYTHON_IDENTITY_TOKEN")
if identity_token:
    sigstore_sign_args.extend(["--identity-token", identity_token])

client_id = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_ID")
if client_id:
    sigstore_sign_args.extend(["--oidc-client-id", client_id])

client_secret = os.getenv("GHA_SIGSTORE_PYTHON_OIDC_CLIENT_SECRET")
if client_secret:
    sigstore_sign_args.extend(["--oidc-client-secret", client_secret])

fulcio_url = os.getenv("GHA_SIGSTORE_PYTHON_FULCIO_URL")
if fulcio_url:
    sigstore_sign_args.extend(["--fulcio-url", fulcio_url])

rekor_url = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_URL")
if rekor_url:
    sigstore_global_args.extend(["--rekor-url", rekor_url])

ctfe = os.getenv("GHA_SIGSTORE_PYTHON_CTFE")
if ctfe:
    sigstore_sign_args.extend(["--ctfe", ctfe])

rekor_root_pubkey = os.getenv("GHA_SIGSTORE_PYTHON_REKOR_ROOT_PUBKEY")
if rekor_root_pubkey:
    sigstore_global_args.extend(["--rekor-root-pubkey", rekor_root_pubkey])

if os.getenv("GHA_SIGSTORE_PYTHON_STAGING", "false") != "false":
    sigstore_global_args.append("--staging")

verify_cert_identity = os.getenv("GHA_SIGSTORE_PYTHON_VERIFY_CERT_IDENTITY")
if enable_verify and not verify_cert_identity:
    _fatal_help("verify-cert-identity must be specified when verify is enabled")
elif not enable_verify and verify_cert_identity:
    _fatal_help("verify-cert-identity cannot be specified without verify: true")
elif verify_cert_identity:
    sigstore_verify_args.extend(["--cert-identity", verify_cert_identity])

verify_oidc_issuer = os.getenv("GHA_SIGSTORE_PYTHON_VERIFY_OIDC_ISSUER")
if enable_verify and not verify_oidc_issuer:
    _fatal_help("verify-oidc-issuer must be specified when verify is enabled")
elif not enable_verify and verify_oidc_issuer:
    _fatal_help("verify-oidc-issuer cannot be specified without verify: true")
elif verify_oidc_issuer:
    sigstore_verify_args.extend(["--cert-oidc-issuer", verify_oidc_issuer])

verify_certificate_chain = os.getenv("GHA_SIGSTORE_PYTHON_VERIFY_CERTIFICATE_CHAIN")
if not enable_verify and verify_certificate_chain:
    _fatal_help("verify-certificate-chain cannot be specified without verify: true")
elif verify_certificate_chain:
    sigstore_verify_args.extend(["--certificate-chain", verify_certificate_chain])

if enable_verify:
    sigstore_verify_args.append(project_path)

sigstore_sign_args.append(project_path)

_debug(f"signing: ansible-sign {[str(a) for a in sigstore_sign_args]}")

sign_status = subprocess.run(
    _ansible_sign_sigstore(sigstore_global_args, sigstore_sign_args),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env={**os.environ, **sigstore_python_env},
)

_debug(sign_status.stdout)

if sign_status.returncode == 0:
    _summary("🎉 ansible-sign signing exited successfully")
else:
    _summary("❌ ansible-sign failed to sign package")

verify_status = None
if sign_status.returncode == 0 and enable_verify:
    _debug(f"verifying: ansible-sign {[str(a) for a in sigstore_verify_args]}")

    verify_status = subprocess.run(
        _ansible_verify_sigstore(sigstore_global_args, sigstore_verify_args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, **sigstore_python_env},
    )

    _debug(verify_status.stdout)

if verify_status is None:
    # Don't add anything to the summary if verification is disabled.
    if enable_verify:
        _summary("❌ ansible-sign verification skipped due to failed signing")
elif verify_status.returncode == 0:
    _summary("🎉 ansible-sign verification exited successfully")
else:
    _summary("❌ ansible-sign failed to verify project")


_log(sign_status.stdout)
_summary(_template("ansible-sign-sign").substitute(output=sign_status.stdout))

if verify_status is not None:
    _log(verify_status.stdout)
    _summary(_template("ansible-sign-verify").substitute(output=verify_status.stdout))

if sign_status.returncode != 0:
    assert verify_status is None
    sys.exit(sign_status.returncode)

# If signing didn't fail, then we check the verification status, if present.
if verify_status is not None:
    sys.exit(verify_status.returncode)
