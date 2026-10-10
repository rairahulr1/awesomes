## Purpose

Present the generated entry index as searchable, filterable views that show who vouched for each entry, without diluting the hand-written list pages that carry the site's authority.

## ADDED Requirements

### Requirement: Entries are searchable and filterable

Readers SHALL be able to search entries by text and filter by source list and category. Filters SHALL combine, so narrowing by source and then by text narrows both.

Search SHALL match an entry's name, description and source attribution, so a reader can find an entry by the words the curator used.

#### Scenario: Text search matches curator wording

- **WHEN** a reader searches for text that appears in a source list's description of a repository
- **THEN** that entry is returned

#### Scenario: Filters combine

- **WHEN** a reader selects a source list and then types a search term
- **THEN** the results satisfy both the source filter and the text query

#### Scenario: No matches is stated plainly

- **WHEN** a query returns no entries
- **THEN** the view states that nothing matched rather than rendering empty

### Requirement: Source attribution is visible on every entry

Every entry view SHALL name the source list or lists that mention the repository. Entries not yet enriched SHALL be visibly distinguished from entries with verified metadata.

The view SHALL NOT imply that this site has verified a repository is maintained, safe, or good.

#### Scenario: Entry shows its vouchers

- **WHEN** an entry is shown
- **THEN** the source list or lists that mention it are named

#### Scenario: Single-source corpus is visible

- **WHEN** the index is dominated by one source list
- **THEN** that distribution is not hidden by an unweighted ranking presented as general relevance

### Requirement: List pages remain the canonical surface

Per-list pages SHALL remain the canonical URLs for their content. Entry views SHALL declare a canonical URL pointing at the relevant list page, so entry views do not compete with the hand-written pages for search indexing.

#### Scenario: Entry view declares its canonical

- **WHEN** an entry view is served
- **THEN** it declares a canonical URL on the corresponding source list page

#### Scenario: List page content is unchanged

- **WHEN** this index is added
- **THEN** the existing per-list pages keep their content, URLs and canonical URLs

### Requirement: Entry views are filter state, not standalone pages

Entries SHALL render as filterable views over the index rather than as one independently indexed URL per entry.

#### Scenario: Filtering does not multiply indexed pages

- **WHEN** a reader filters the index
- **THEN** the filtered result is not itself a separately addressable indexed page

### Requirement: The index reports its own provenance

The entry index SHALL display when it was last generated and from which sources, so a reader can judge how current it is.

#### Scenario: Generated-at stamp is shown

- **WHEN** the entry index is viewed
- **THEN** the generation timestamp and the set of source lists are shown