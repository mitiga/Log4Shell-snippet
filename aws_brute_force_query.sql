SELECT username, sourceipaddress, count(*) as counter FROM "lab"."cloudtrail" 
where eventsource = 'signin.amazonaws.com'
and eventname = 'ConsoleLogin'
and consolelogin = 'Failure'
group by username, sourceipaddress
order by counter desc 
limit 20;
