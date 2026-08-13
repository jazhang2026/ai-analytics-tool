# Adding a New Feature or Making a Change
## Step 1: Specify


/speckit-specify <description of the new feature or change>

This creates a new numbered spec directory (e.g., specs/002-new-feature/) with its own spec.md.

## Step 2: Clarify (optional)


/speckit-clarify
Resolves ambiguities in the new spec before planning.

## Step 3: Plan


/speckit-plan <any technical constraints for this feature>
Generates plan.md, research.md, data-model.md, contracts/, quickstart.md for the new feature.

## Step 4: Tasks


/speckit-tasks
Generates tasks.md with implementation tasks scoped to the new feature.

## Step 5: Implement


/speckit-implement
Executes the tasks and writes code.

## Step 6: Converge (optional)


/speckit-converge
After implementation, checks if anything was missed and appends remaining work as new tasks.

## Two Scenarios
| Scenario | Approach |
|----------|----------|
| New feature (new screen, new role, etc.) | Full workflow: /speckit-specify → /speckit-plan → /speckit-tasks → /speckit-implement |
| Bug fix or small tweak | Skip the full process — just describe the fix and I'll implement it directly |

## Example: Adding Email Notifications


/speckit-specify Add email notification when analytics request completes
/speckit-plan Use SendGrid for email delivery
/speckit-tasks
/speckit-implement

## How Specs Are Organized


specs/
├── 001-data-analytics-platform/   # Your current feature
├── 002-email-notifications/       # Next feature
├── 003-advanced-reporting/        # After that
└── ...
Each spec is independent but can reference entities and APIs from previous specs. The constitution in .specify/memory/constitution.md applies across all features.

## Updating an Existing Spec (Not Recommended)
If you need to change something already implemented in 001-data-analytics-platform, it's usually better to create a new spec (e.g., 002-auth-enhancements) that describes the delta, rather than editing the original spec. This keeps the history clean and each spec independently testable.