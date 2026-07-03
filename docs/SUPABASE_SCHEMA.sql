create table if not exists audit_runs (
  id uuid primary key,
  created_at timestamptz not null default now(),
  protected_attribute text not null,
  target text not null,
  dataset_rows integer not null,
  summary text not null,
  metrics jsonb not null,
  mitigation jsonb not null,
  explanations jsonb not null
);

create index if not exists audit_runs_created_at_idx on audit_runs (created_at desc);
create index if not exists audit_runs_protected_attribute_idx on audit_runs (protected_attribute);
