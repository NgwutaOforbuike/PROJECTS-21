# Security Policy — Global Wealth & Trading OS

## Private-use intent

Global Wealth & Trading OS is intended for the repository owner's personal use. Source-code visibility and deployment access must be configured as private at the hosting-provider level.

## Secrets

Never commit:
- API keys
- broker credentials
- passwords
- private keys
- session tokens
- database credentials
- exchange or market-data entitlement secrets

All secrets must be injected by the deployment platform as environment variables or a managed secrets service.

## Live execution

Live execution is disabled by design. No model, agent, scheduled task or training process may enable live execution or alter the owner's risk mandate.

## Security reporting

If a credential is ever committed:
1. revoke/rotate it immediately;
2. remove it from current source;
3. purge it from Git history where necessary;
4. invalidate affected sessions;
5. review audit logs.

## Data protection

Training artifacts, portfolio records, broker information and decision history must not be written to public build artifacts or frontend bundles.
