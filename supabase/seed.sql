-- Datos de ejemplo mínimos
insert into public.conversations (id, user_id, status)
values
  ('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'active')
on conflict do nothing;
