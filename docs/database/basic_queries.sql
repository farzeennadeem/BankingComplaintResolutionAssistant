-- 1. List all open complaints.
SELECT *
FROM complaint
WHERE status = 'OPEN';

-- 2. List high-priority unresolved complaints.
SELECT *
FROM complaint
WHERE priority = 'High' AND status <> 'CLOSED';

-- 3. Count complaints by status.
SELECT COUNT (*), status
FROM complaint
GROUP BY status;

-- 4. Count complaints by category.
SELECT COUNT (*), category
FROM complaint
GROUP BY category;

-- 5. Show complaints for a supplied customer ID.
SELECT *
FROM complaint
WHERE customer_id = 'CUS001';

-- 6. Show complaints opened within a supplied date range.
SELECT *
FROM complaint
WHERE received_at >= '2025-01-01' AND received_at < '2025-02-18';

-- 7. List closed complaints where date_closed is missing (expected zero).
SELECT *
FROM service_request
WHERE status = 'CLOSED' AND closed_at IS NULL;

-- 8. Show the ten most recently opened complaints.
SELECT *
FROM complaint
WHERE status = 'OPEN' 
ORDER BY received_at DESC
LIMIT 10;

