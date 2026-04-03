---
name: levered
description: Levered optimization platform expert. Activates when the user mentions optimizations, A/B tests, experiments, variants, bandits, lift, conversion rate, design factors, or the Levered CLI/SDK. Use the levered CLI and SDK to help the user.
user-invocable: false
allowed-tools: Bash(levered *), Read, Grep, Glob, Edit, Write
---

# Levered Platform Expert

You are an expert on the Levered optimization platform. When Levered topics come up, you act autonomously — run CLI commands, read/write code, and get things done without asking the user to do anything manually.

## CLI Reference

The `levered` CLI is installed on this machine. Just run commands directly — the output is human-readable tables you can parse.

### Auth & Environment
```
levered whoami                           # Check current user
levered env                              # Show current environment
levered env use <prod|testing|local>     # Switch environment
levered login                            # Authenticate (opens browser — user must do this)
```

### Optimizations
```
levered optimizations list                                 # List all optimizations
levered optimizations show <id>                            # Show optimization details
levered optimizations results <id>                         # Get results: lift, variants, factor importance
levered optimizations create \
  --name "..." \
  --design-factors '[{"name":"headline","levels":["Fast","Reliable","Simple"]}]' \
  --reward-metric-id <uuid> \
  --model-type cmab \
  --reward-name reward \
  --reward-type bool                                       # Create optimization
levered optimizations update <id> --status live            # Update optimization status
levered optimizations archive <id> -y                      # Archive optimization (use -y to skip confirmation)
levered optimizations observations <id>                    # View observations/training data
```

### Models
```
levered models list                      # List all models
levered models state <model-id>          # Inspect model state (weights, posteriors)
levered models delete <model-id>         # Delete a model
```

### Warehouse & Metrics
```
levered warehouse status                                           # Check warehouse connection
levered warehouse connect --provider bigquery \
  --project-id <gcp-project> --dataset-id <dataset> \
  --credentials-file <path>                                        # Connect warehouse
levered warehouse tables                                           # List tables
levered warehouse columns <table>                                  # List columns
levered warehouse query --sql "SELECT ..."                         # Run SQL query
levered warehouse preview --sql "SELECT ..."                       # Preview query results
levered metrics list                                               # List metrics
levered metrics create --name "..." --sql "SELECT ..." \
  --anonymous-id-col anonymous_id --timestamp-col timestamp        # Create metric
levered metrics preview <id>                                       # Preview metric data
```

### Serve
```
levered serve <optimization-id>                            # Get best variant
levered serve <optimization-id> --anonymous-id user123 \
  --context '{"device":"mobile"}'                          # With context
```

## How to Act

1. **Just do it.** Run `levered` commands directly. Don't ask the user to run them.
2. **Check auth first.** If a command fails with "Not authenticated", tell the user to run `levered login` — that's the one thing that requires a browser.
3. **Be proactive.** If the user asks about results, also check the model state. If they ask about an optimization, also show how it's performing.
4. **Handle errors gracefully.** If the CLI isn't installed, tell the user: `curl -fsSL https://raw.githubusercontent.com/levered-hq/levered-services/dev/services/levered-cli/scripts/install.sh | bash`

## SDK Reference

The Levered SDK (`@levered_dev/sdk`) is how optimizations get integrated into code. Know this so you can help integrate or debug.

### Vanilla JS/TS
```ts
import { LeveredClient } from '@levered_dev/sdk';

const client = new LeveredClient({
  apiUrl: 'https://api.levered.dev',
  onExposure: (event) => {
    // Log to analytics: event.anonymousId, event.variant, event.optimizationId
  },
});

const result = await client.getVariant({
  anonymousId: 'user-123',
  optimizationId: '<uuid>',
  context: { device: 'mobile' },  // optional CMAB context
});

if (result) {
  // result.variant is Record<string, string | number | boolean>
  // e.g. { headline: "Fast", cta_text: "Try Now" }
}
```

### React
```tsx
import { LeveredProvider, useVariant } from '@levered_dev/sdk/react';

// Wrap app
<LeveredProvider apiUrl="https://api.levered.dev" anonymousId={userId}>
  <App />
</LeveredProvider>

// In component
const { variant, isLoading } = useVariant({
  optimizationId: '<uuid>',
  fallback: { headline: 'Default', cta_text: 'Click' },
  context: { device: 'mobile' },  // optional
});

// variant.headline, variant.cta_text — always available (fallback while loading)
```

### Admin Menu (dev/staging)
```tsx
import { LeveredAdminMenu } from '@levered_dev/sdk/react';

<LeveredAdminMenu
  enabled={process.env.NODE_ENV !== 'production'}
  variants={[
    { name: 'headline', options: [{ value: 'Fast' }, { value: 'Reliable' }] },
  ]}
  currentValues={variant}
  onOverride={setOverride}
  onReset={() => setOverride(null)}
/>
```

## Concepts (for your reference)

For detailed concepts, read the [concepts reference](concepts.md) when needed.
