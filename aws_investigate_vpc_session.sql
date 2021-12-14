select * from "lab"."vpc_flow_logs" 
where srcaddr = '10.111.160.62'
and dstaddr = '10.111.155.37'
order by start, dstaddr, dstport
