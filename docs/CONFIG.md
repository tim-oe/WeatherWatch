# system configuration

## application config
- [weatherwatch.yml](/config/weatherwatch.yml?raw=true)
    - the intention of this is to contain defauts and allow for overrides via environment variables
    - see file for where env var overrides can be used
    - TODO: move sensor config to DB
- processing intervals 
    - its recommended not going below 5 minutes
- no default database creds only from env vars
    - see [setup](/docs/SETUP.md)        