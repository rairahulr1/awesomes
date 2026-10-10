## Purpose

Turn the ten indexed awesome-list READMEs into structured, deduplicated repository entries with an attributable description, so the corpus is searchable instead of trapped inside large markdown files.

## ADDED Requirements

### Requirement: Entry extraction across source link formats

The indexer SHALL extract repository entries from every indexed source list, and SHALL support each markdown link format those sources use: table rows, bulleted entries with a description tail, repository-relative paths, and per-project prose sections.

Each format SHALL have an automated fixture test using a representative excerpt of that source's real README. A format with no fixture test SHALL be treated as unimplemented, not as empty.

#### Scenario: Table-format source is parsed

- **WHEN** a source README contains entries as markdown table rows with a link, a name and a description cell
- **THEN** each row yields one entry with link, name and description

#### Scenario: Bulleted sources are parsed

- **WHEN** a source README contains bulleted entries whose description follows the link, with or without emphasis markers
- **THEN** each bullet yields one entry and the description is captured without its trailing punctuation or emphasis characters

#### Scenario: Format with no fixture test is refused

- **WHEN** a source link format has no corresponding fixture test
- **THEN** extraction for that source fails with an explicit error naming the format

### Requirement: Repository-relative link resolution

The indexer SHALL resolve a link that is relative to the source repository into an absolute GitHub URL, using that source repository as the base.

An entry whose relative link cannot be resolved SHALL be reported as unresolved. Unresolved entries SHALL NOT be silently discarded, because silent loss is indistinguishable from a source having no entries.

#### Scenario: Relative directory link resolves

- **WHEN** a source README links to `agent_skills/project-graveyard/` rather than an absolute URL
- **THEN** the entry link is the absolute URL under that source repository
- **AND** the entry is included in the index

#### Scenario: Unresolvable link is reported

- **WHEN** a link is neither absolute nor resolvable against the source repository's base URL
- **THEN** the entry is recorded as unresolved with the offending link text
- **AND** the run reports a count of unresolved links

### Requirement: Description capture and attribution

An entry's description SHALL be the wording used by the source list that mentions it, preserved without rewriting.

Every entry SHALL record the source list or lists that mention it. When two sources describe the same repository differently, the entry SHALL retain both descriptions with their attributions rather than merging them.

#### Scenario: Description is not restated as site fact

- **WHEN** an entry is published
- **THEN** its description is presented as the wording of the named source list
- **AND** the page carries no claim that this site verified the description

#### Scenario: Repository appears in two sources with different wording

- **WHEN** the same repository is mentioned by two source lists with different descriptions
- **THEN** one entry is created with both descriptions retained, each attributed to its source

### Requirement: Deduplication on canonical repository identity

The indexer SHALL deduplicate entries on canonical `owner/repo`, case-insensitively, and SHALL strip only a trailing `.git` suffix when normalising.

A repository mentioned by multiple source lists SHALL produce one entry carrying all its sources.

#### Scenario: Duplicate repository collapses to one entry

- **WHEN** the same repository appears in two source lists
- **THEN** one entry exists with two recorded sources

#### Scenario: Normalisation does not strip name characters

- **WHEN** a repository name ends in the letters `g`, `i`, `t` or the word `git` as part of its real name
- **THEN** normalisation removes only a literal `.git` suffix and preserves the rest of the name

#### Scenario: Embedded media paths are not entries

- **WHEN** a source README links to a GitHub-hosted attachment path rather than a repository
- **THEN** no entry is created for it

### Requirement: Extraction output is reviewable

Extraction SHALL write a generated data file containing every entry, and the run SHALL report entry counts per source list.

Extraction SHALL support a mode that reports what it would produce without writing, so the output can be reviewed before anything downstream depends on it.

#### Scenario: Dry run writes nothing

- **WHEN** extraction runs in report-only mode
- **THEN** no generated data file is written
- **AND** per-source entry counts are reported

#### Scenario: An unexpectedly small result is visible

- **WHEN** extraction returns markedly fewer entries than the source's previous extraction
- **THEN** the run reports the per-source change so a parser regression is visible rather than silent