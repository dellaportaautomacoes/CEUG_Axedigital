-- Axé Digital · banco do CEUG. Cole TUDO no Supabase: menu "SQL Editor" > New query > Run.
create table if not exists perfis (
  user_id uuid primary key references auth.users on delete cascade,
  email text,
  papel text not null default 'membro' check (papel in ('membro','admin')),
  criado_em timestamptz default now()
);
create table if not exists pontos_enviados (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  autor text,
  titulo text,
  texto text not null,
  cat text, ent text,
  tipo text not null default 'ponto',
  status text not null default 'pendente' check (status in ('pendente','aprovado','rejeitado')),
  criado_em timestamptz default now()
);
alter table perfis enable row level security;
alter table pontos_enviados enable row level security;

create or replace function is_admin() returns boolean
language sql security definer stable set search_path = public as
$$ select exists (select 1 from perfis where user_id = auth.uid() and papel = 'admin') $$;

create or replace function novo_usuario() returns trigger
language plpgsql security definer set search_path = public as
$$ begin insert into perfis (user_id, email) values (new.id, new.email); return new; end $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute function novo_usuario();

drop policy if exists perfis_ver on perfis;
create policy perfis_ver on perfis for select to authenticated using (user_id = auth.uid() or is_admin());

drop policy if exists pe_ver on pontos_enviados;
create policy pe_ver on pontos_enviados for select to authenticated
  using (status = 'aprovado' or user_id = auth.uid() or is_admin());
drop policy if exists pe_enviar on pontos_enviados;
create policy pe_enviar on pontos_enviados for insert to authenticated
  with check (user_id = auth.uid() and status = 'pendente');
drop policy if exists pe_decidir on pontos_enviados;
create policy pe_decidir on pontos_enviados for update to authenticated using (is_admin()) with check (is_admin());
drop policy if exists pe_apagar on pontos_enviados;
create policy pe_apagar on pontos_enviados for delete to authenticated
  using (is_admin() or (user_id = auth.uid() and status = 'pendente'));
-- Depois que o responsável criar a conta no app, rode (troque o e-mail):
-- update perfis set papel = 'admin' where email = 'EMAIL_DO_RESPONSAVEL';
