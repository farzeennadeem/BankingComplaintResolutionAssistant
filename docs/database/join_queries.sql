-- 1. Show each complaint with customer name.
SELECT complaint.*, customer.first_name, customer.last_name
FROM complaint
JOIN customer
ON complaint.customer_id  = customer.customer_id;

-- 2. Add optional account type without dropping complaints that have no account.
SELECT c.complaint_id, cu.first_name, cu.last_name, a.account_type
FROM complaint c
JOIN customer cu     ON cu.customer_id = c.customer_id
LEFT JOIN account a  ON a.account_id  = c.account_id;

-- 3. Verify distinct complaint count before and after joins.
SELECT COUNT(complaint_id)
FROM complaint;

SELECT COUNT(DISTINCT complaint.complaint_id)
FROM complaint
JOIN customer
ON complaint.customer_id  = customer.customer_id
JOIN account
ON complaint.customer_id = account.customer_id;


-- 4. Create complaint_analyst_view containing only justified fields.
CREATE VIEW complaint_analyst_view AS
SELECT c.complaint_id, c.customer_id, c.account_id, a.account_type,
       c.channel, c.category, c.priority, c.status, c.received_at,
       c.assigned_analyst_id,
       e.first_name || ' ' || e.last_name AS analyst_name
FROM complaint c
LEFT JOIN account a  ON a.account_id  = c.account_id
LEFT JOIN employee e ON e.employee_id = c.assigned_analyst_id;

SELECT *
FROM complaint_analyst_view;





hello world hello world hello world hello wor hello world hello world hello world hello world he
hello world hello world hello world hello world anisa anisa anisa jasmine anisa jasmine chaudhry
anisa jasmine chaudhry anisa jasmine chaudhry anisa jasmine chaudhry anisa jasmine chaudhry anisa jasmine cahudhry
anisa jasmine chaudhry chaudhry
anisa jasmine chaudhry
anisa jasmine chaudhry
anisa jasmine chaudhry anisa jasmine anisa jasmine chaudhry
anisa jasmine chaudhry
anisa jasmine chaudhry
anisa jasmine chaudhry
anisa jasmine chaudhry
anisa jasmine chaudhry
ani ani ani 
leaving drinks
pub tech uk office
5 million pound
shepard brewery
train back
funding events
fdm partnership
university degrees
continuity
gold course
new course
anisa anisa
sprints programs
pickle sandwich
boring
lunch 
2 kids
pasta tuna
nothing going for him
school kids
jamie oliver
bbq slow cooker
curry fan
fish or steak
olive oil
nonna italian
england italy rugby
rome and florence
arena venice
detroit
anisa




