select target_ip, target_port from "lab"."alb_logs"
where
(request_url like '%jndi:%' or
request_url like '%${::-j}${%' or
request_url like '%${::-l}${::-d}${::-a}${::-p}%' or
request_url like '%${base64:JHtqbmRp%' or
user_agent like '%jndi:%' or
user_agent like '%${::-j}${%' or
user_agent like '%${::-l}${::-d}${::-a}${::-p}%' or
user_agent like '%${base64:JHtqbmRp%')
group by target_ip, target_port;
