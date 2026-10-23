# Anthropic OSS Scanner integration

This directory prepares VALEO NeuroERP 3.0 for Anthropic's OSS Scanner.

- `Dockerfile` installs the Python and pnpm dependency trees, compiles the
  application and leaves the checkout ready for an offline security analysis.
- `threat_model.md` defines trust boundaries, high-value components, severity
  rules and safe reporting expectations.

Build locally from the repository root:

```bash
docker build -f .oss-scanner/Dockerfile -t valeo-neuroerp-oss-scanner .
docker run --rm --network none -it valeo-neuroerp-oss-scanner bash
```

Enrollment is completed in `anthropics/oss-scanner` with a single
`projects/valeo-neuroerp-3/project.yaml`:

```yaml
repo: https://github.com/JochenWeerda/VALEO-NeuroERP-3.0#main
primary_contact: <VERIFIED_PUBLIC_SECURITY_EMAIL>
homepage: https://github.com/JochenWeerda/VALEO-NeuroERP-3.0
disabled: false
dockerfile: .oss-scanner/Dockerfile
threat_model: .oss-scanner/threat_model.md
```

The contact address is deliberately not stored as a placeholder in an active
enrollment. Anthropic publishes this address and sends build problems and
security reports to it. A core maintainer must also complete Anthropic's
one-time contributor license agreement on the enrollment pull request.
