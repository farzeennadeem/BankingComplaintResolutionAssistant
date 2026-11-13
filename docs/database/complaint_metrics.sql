-- Complaint volume by status, category and month.
SELECT COUNT(DISTINCT customer_id)
FROM complaint_analyst_view;

SELECT COUNT(complaint_id) complaints, category, COUNT(DISTINCT customer_id) distinct_customers
FROM complaint_analyst_view
GROUP BY category;

SELECT COUNT(complaint_id) complaints, csh.new_status current_status
FROM complaint_status_history csh
GROUP BY csh.new_status;

SELECT COUNT(complaint_id) AS Complaints, strftime('%Y, %m', received_at) AS Month, COUNT(DISTINCT customer_id) AS DistinctCustomers
FROM complaint_analyst_view
GROUP BY strftime('%Y, %m', received_at);

-- Open an escalated backlog.
SELECT COUNT(complaint_id) complaints, new_status currentStatus, changed_at, ROUND(JULIANDAY('now') - JULIANDAY(csh.changed_at)) daysSinceChange
FROM complaint_status_history csh
GROUP BY new_status;

SELECT csh.complaint_id, csh.new_status status, csh.changed_at complaintClosedAt, c.received_at complaintReceivedAt, ROUND(JULIANDAY(csh.changed_at) - JULIANDAY(c.received_at)) daysToSolve
FROM complaint_status_history csh
JOIN complaint c
ON c.complaint_id = csh.complaint_id
WHERE csh.new_status = 'CLOSED';
