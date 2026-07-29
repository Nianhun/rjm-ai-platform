create table if not exists formula_request (
  request_id text primary key,
  goal text not null,
  dosage_form text,
  constraints_json text not null default '{}',
  requester text,
  source text not null default 'management_console',
  created_at text not null default current_timestamp
);

create table if not exists formula_candidate (
  id integer primary key auto_increment,
  formula_id text not null,
  request_id text not null,
  goal text not null,
  status text not null default 'candidate',
  formula_json text not null,
  ingredient_ids_json text not null default '[]',
  evidence_ids_json text not null default '[]',
  risk_notes_json text not null default '[]',
  score_total real,
  score_json text not null default '{}',
  created_at text not null default current_timestamp,
  foreign key (request_id) references formula_request(request_id)
);

create index if not exists idx_formula_candidate_formula_id
  on formula_candidate(formula_id);

create index if not exists idx_formula_candidate_request_id
  on formula_candidate(request_id);

create table if not exists formula_screening (
  id integer primary key auto_increment,
  formula_id text not null,
  engineer text not null,
  decision text not null,
  reason text not null,
  modified_ingredients_json text not null default '[]',
  created_at text not null default current_timestamp
);

create index if not exists idx_formula_screening_formula_id
  on formula_screening(formula_id);

create table if not exists experiment_feedback (
  id integer primary key auto_increment,
  formula_id text not null,
  batch_no text not null,
  result text not null,
  ingredient_ids_json text not null default '[]',
  metrics_json text not null default '{}',
  issues_json text not null default '[]',
  engineer_conclusion text,
  engineer text,
  created_at text not null default current_timestamp
);

create index if not exists idx_experiment_feedback_formula_id
  on experiment_feedback(formula_id);

create table if not exists experiment_batch (
  id integer primary key auto_increment,
  batch_no text not null unique,
  formula_id text not null,
  stage text not null,
  owner text not null,
  metrics_json text not null default '{}',
  issues_json text not null default '[]',
  conclusion text,
  status text not null default 'planned',
  created_at text not null default current_timestamp
);

create index if not exists idx_experiment_batch_formula_id
  on experiment_batch(formula_id);

create table if not exists learned_weight (
  id integer primary key auto_increment,
  goal text not null,
  target_type text not null,
  target_key text not null,
  weight real not null,
  evidence_count integer not null default 0,
  source text not null default 'experiment_feedback',
  calculation_note text,
  updated_at text not null default current_timestamp
);

create unique index if not exists idx_learned_weight_unique_target
  on learned_weight(goal, target_type, target_key);

create index if not exists idx_learned_weight_goal_type
  on learned_weight(goal, target_type);

create table if not exists evidence_record (
  evidence_id text primary key,
  source_type text not null,
  title text not null,
  summary text,
  source_url text,
  metadata_json text not null default '{}',
  imported_at text not null default current_timestamp
);

create table if not exists knowledge_import_batch (
  batch_id text primary key,
  source_system text not null default 'yuxi',
  source_files_json text not null default '{}',
  output_files_json text not null default '{}',
  ingredient_count integer not null default 0,
  relation_count integer not null default 0,
  evidence_count integer not null default 0,
  governance_notes_json text not null default '[]',
  imported_at text not null default current_timestamp
);

create table if not exists ingredient_alias (
  id integer primary key auto_increment,
  ingredient_id text not null,
  alias text not null,
  alias_type text not null default 'name',
  source text not null default 'yuxi',
  created_at text not null default current_timestamp
);

create unique index if not exists idx_ingredient_alias_unique
  on ingredient_alias(ingredient_id, alias, alias_type);

create table if not exists raw_material_sku (
  sku_id text primary key,
  ingredient_id text not null,
  supplier_id text not null,
  supplier_name text,
  specification text,
  price_currency text,
  price_amount_per_kg real,
  moq_kg real,
  lead_time_days integer,
  qualification_files_json text not null default '[]',
  sample_status text,
  quality_rating real,
  updated_at text not null default current_timestamp
);

create index if not exists idx_raw_material_sku_ingredient_id
  on raw_material_sku(ingredient_id);

create table if not exists procurement_recommendation (
  id integer primary key auto_increment,
  formula_id text not null,
  ingredient_id text not null,
  sku_id text,
  supplier_id text,
  status text not null,
  procurement_score real,
  recommendation_json text not null default '{}',
  created_at text not null default current_timestamp,
  foreign key (sku_id) references raw_material_sku(sku_id)
);

create index if not exists idx_procurement_recommendation_formula_id
  on procurement_recommendation(formula_id);
