## Purpose

Keep per-entry volatile facts — star counts, when this site last verified a link, and when the upstream list last changed — current, dated, and honest about failure.

## ADDED Requirements

### Requirement: Entries carry dated volatile facts

Every entry SHALL record a star count, a `verified_at` date recording when this site last confirmed the link, and a `source_updated_at` date recording the upstream source list's last commit.

A star count SHALL be labelled a point-in-time snapshot wherever it is displayed. `verified_at` and `source_updated_at` SHALL be stored as distinct fields because they answer different questions: when this site checked, versus when upstream changed.

#### Scenario: Entry displays both dates distinctly

- **WHEN** an entry is rendered
- **THEN** the star count is labelled as a snapshot as of `verified_at`
- **AND** the upstream list's last change is shown separately and not conflated with `verified_at`

#### Scenario: Entry with no star count yet

- **WHEN** an entry has been extracted but not yet enriched
- **THEN** it renders without a star count rather than showing zero

### Requirement: Star enrichment is authenticated

Enrichment SHALL send a GitHub API token. Without a token the run SHALL refuse to start rather than proceed at the anonymous rate limit.

#### Scenario: Missing token blocks the run

- **WHEN** enrichment runs with no token available
- **THEN** the run fails with a message stating that a token is required
- **AND** no entries are rewritten

### Requirement: Enrichment is resumable and checkpointed

Enrichment SHALL record completed work so an interrupted run resumes instead of restarting, and SHALL be safe to run repeatedly.

#### Scenario: Interrupted run resumes

- **WHEN** enrichment stops partway through
- **THEN** a later run continues from the last completed point rather than repeating completed lookups

### Requirement: Failed lookups preserve the previous value

When a lookup fails for an entry, enrichment SHALL leave that entry's previous value in place and SHALL report the failure. It SHALL NOT write an empty, zero or decremented star count.

#### Scenario: Repository has been deleted upstream

- **WHEN** the GitHub API returns 404 for an entry's repository
- **THEN** the entry's previous star count is preserved
- **AND** the entry is marked unavailable
- **AND** the failure is reported

#### Scenario: Transient API error

- **WHEN** a lookup fails for a transient reason such as rate limiting
- **THEN** the previous value is preserved and the entry is retried on the next run

### Requirement: Refresh runs on a schedule and commits only real changes

A scheduled refresh SHALL run automatically and SHALL commit only when values actually changed, so an unchanged run produces no repository noise.

#### Scenario: Unchanged run produces no commit

- **WHEN** a scheduled refresh finds no changed values
- **THEN** no commit is created

#### Scenario: Changed values are committed

- **WHEN** a scheduled refresh updates star counts
- **THEN** only the generated data file is committed