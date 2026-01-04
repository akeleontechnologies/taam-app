# Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      page.tsx (91 lines)                        │
│                   Main Chart Viewer Page                        │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─── Uses Hooks ──────────────────────────────────┐
             │                                                  │
             │   ┌──────────────────────────────────┐          │
             │   │  useChartData()                  │          │
             │   │  - Fetches dataset               │          │
             │   │  - Fetches summary charts        │          │
             │   │  - Fetches respondent charts     │          │
             │   │  - Pagination logic              │          │
             │   │  - Returns: dataset, charts,     │          │
             │   │    summaryCharts, filterOptions  │          │
             │   └──────────────────────────────────┘          │
             │                                                  │
             │   ┌──────────────────────────────────┐          │
             │   │  useFilteredDistribution()       │          │
             │   │  - Manages filter state          │          │
             │   │  - Fetches filtered data         │          │
             │   │  - Returns: filters,             │          │
             │   │    handleFilterChange            │          │
             │   └──────────────────────────────────┘          │
             │                                                  │
             └─── Renders Components ─────────────────────────┘
                  │
                  ├─── DistributionChart ────────────────────┐
                  │    │                                      │
                  │    ├─ FilterPanel                        │
                  │    │  (Age/Gender/Emirate dropdowns)     │
                  │    │                                      │
                  │    ├─ Summary Stats Cards                │
                  │    │  (Total Respondents, Personas)      │
                  │    │                                      │
                  │    ├─ Bar Chart                           │
                  │    │  (Persona Distribution)             │
                  │    │                                      │
                  │    └─ Persona Grid                        │
                  │       (Color-coded badges)               │
                  │                                           │
                  └─── RespondentRadarCard (x20) ───────────┐
                       │                                     │
                       ├─ Radar Chart                        │
                       │  (TAAM Axes)                        │
                       │                                     │
                       └─ Expandable Details                 │
                          - Survey Answers (Q1-Q26)         │
                          - Computed Axes Values            │
                                                             │
┌──────────────────────────────────────────────────────────────────┐
│                     Shared Libraries                             │
├──────────────────────────────────────────────────────────────────┤
│  lib/charts/                                                     │
│    ├─ types.ts      (ChartSpec, Dataset, FilterOptions, etc.)   │
│    └─ constants.ts  (PERSONA_COLORS, CHARTS_PER_PAGE)           │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Action (Filter Change)
     │
     ▼
FilterPanel.onChange
     │
     ▼
page.tsx.onFilterChange
     │
     ▼
useFilteredDistribution.handleFilterChange
     │
     ├─ Update local filter state
     │
     ├─ Fetch filtered data from API
     │      /api/charts/dataset/{uid}/filtered-distribution/
     │
     └─ Call updateSummaryChart callback
            │
            ▼
       useChartData.updateSummaryChart
            │
            ▼
       Update summaryCharts state
            │
            ▼
       DistributionChart re-renders with new data
```

## Component Hierarchy

```
ChartViewPage
├── Header
│   ├── Back Button
│   ├── Dataset Title
│   └── Respondent Count
│
├── DistributionChart
│   ├── FilterPanel
│   │   ├── Age Dropdown
│   │   ├── Gender Dropdown
│   │   └── Emirate Dropdown
│   │
│   ├── Summary Stats
│   │   ├── Total Respondents Card
│   │   └── Unique Personas Card
│   │
│   ├── Bar Chart
│   │   └── Recharts BarChart
│   │
│   └── Persona Grid
│       └── Persona Cards (A-J)
│
└── Respondent List
    ├── Section Header
    │
    ├── Respondent Grid
    │   └── RespondentRadarCard (x20)
    │       ├── Header (Title, Persona Badge)
    │       ├── Radar Chart
    │       └── Expandable Details
    │           ├── Survey Answers
    │           └── Computed Axes
    │
    └── Load More Button
```

## File Organization

```
frontend/
├── app/dashboard/charts/[uid]/
│   └── page.tsx                    ← Main page (91 lines)
│
├── components/charts/
│   ├── index.ts                    ← Barrel export
│   ├── FilterPanel.tsx             ← Filter dropdowns (58 lines)
│   ├── RespondentRadarCard.tsx     ← Individual chart (115 lines)
│   └── DistributionChart.tsx       ← Summary chart (110 lines)
│
├── hooks/
│   ├── useChartData.ts             ← Data fetching (147 lines)
│   └── useFilteredDistribution.ts  ← Filter logic (66 lines)
│
└── lib/charts/
    ├── index.ts                    ← Barrel export
    ├── types.ts                    ← TypeScript types (61 lines)
    └── constants.ts                ← Constants (15 lines)
```

## Benefits

### Before Refactoring
- ❌ 519 lines in single file
- ❌ All logic in one component
- ❌ Hard to test individual pieces
- ❌ Difficult to reuse components
- ❌ Poor separation of concerns

### After Refactoring
- ✅ 91 line main component (82% reduction)
- ✅ 3 reusable components
- ✅ 2 custom hooks for logic
- ✅ Shared types and constants
- ✅ Easy to test and maintain
- ✅ Clear separation of concerns
