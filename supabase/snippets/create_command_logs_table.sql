--Copie e cole exatamente este SQL no SQL Editor do Studio (http://127.0.0.1:54323) e execute:
-- Fase 2: Banco Profissional - command_logs
-- DROP TABLE IF EXISTS public.command_logs; -- Descomente se quiser resetar

alter table public.command_logs
add column if not exists user_id uuid,
add column if not exists email text;

create index if not exists idx_command_logs_user_id
on public.command_logs(user_id);

create index if not exists idx_command_logs_email
on public.command_logs(email);

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'command_logs_user_id_fkey'
    ) then
        alter table public.command_logs
        add constraint command_logs_user_id_fkey
        foreign key (user_id)
        references auth.users (id);
    end if;
end $$;

select
    id,
    command,
    response,
    client_ip,
    user_id,
    email,
    created_at
from public.command_logs
order by created_at desc
limit 20;