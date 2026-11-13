--1. Use CASE for unresolved age buckets 0-7, 8-30 and 31+ days.
SELECT
CASE
	WHEN ROUND(JULIANDAY('now') - JULIANDAY(c.received_at)) >= 0 AND ROUND(JULIANDAY('now') - JULIANDAY(c.received_at)) <= 7 THEN '0-7 Days'
	WHEN ROUND(JULIANDAY('now') - JULIANDAY(c.received_at)) >= 8 AND ROUND(JULIANDAY('now') - JULIANDAY(c.received_at)) <= 30 THEN '8-30 Days'
	ELSE '31+ Days'
END AS buckets,
COUNT(csh.complaint_id) totalComplaints
FROM complaint_status_history csh
JOIN complaint c
ON c.complaint_id = csh.complaint_id
WHERE csh.new_status IN ('OPEN', 'IN PROGRESS', 'UNDER REVIEW')
GROUP BY buckets;

--2. Use a CTE to identify repeat complainants.
WITH temp_table AS (
    SELECT 
        customer_id,
        COUNT(complaint_id) AS complaintCount
    FROM complaint
    GROUP BY customer_id
    --HAVING complaintCount > 1
)
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    tt.complaintCount
FROM customer AS c
JOIN temp_table AS tt
    ON c.customer_id = tt.customer_id
ORDER BY tt.complaintCount DESC, c.customer_id;


--3. Use ROW_NUMBER to select latest status per complaint.
WITH ranked_statuses AS (
    SELECT 
        complaint_id,
        new_status,
        changed_at,
        ROW_NUMBER() OVER (
            PARTITION BY complaint_id 
            ORDER BY changed_at DESC
        ) AS rn
    FROM complaint_status_history
)
SELECT 
    complaint_id,
    new_status AS latest_status,
    changed_at AS last_updated
FROM ranked_statuses
WHERE rn = 1;


--4. Rank customers by complaint count.
WITH customer_counts AS (
    SELECT customer_id, COUNT(complaint_id) AS complaint_count
    FROM complaint
    GROUP BY customer_id
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY cc.complaint_count DESC, c.customer_id ASC) AS customer_rank, --lowest customer_id always wins if tie
    c.customer_id,
    c.first_name,
    c.last_name,
    cc.complaint_count
FROM customer_counts AS cc
JOIN customer AS c
    ON cc.customer_id = c.customer_id
ORDER BY customer_rank;

--5.Determine complaint priority classification.
SELECT ROW_NUMBER() OVER (ORDER BY
CASE priority
	WHEN 'Critical' THEN 1
	WHEN 'High' THEN 2
	WHEN 'Medium' THEN 3
	WHEN 'Low' THEN 4
END ASC, received_at ASC)
AS priority_rank, complaint_id, priority, received_at
FROM complaint;

--6.Find customers who submitted more than one complaint.
SELECT COUNT(complaint.complaint_id) totalComp, complaint.customer_id, c.first_name, c.last_name
FROM complaint
JOIN customer c
ON c.customer_id = complaint.customer_id
GROUP BY c.customer_id HAVING totalComp > 1
ORDER BY totalComp DESC;

--7.Rank customers by number of complaints.
WITH customer_counts AS (
    SELECT customer_id, COUNT(complaint_id) AS complaint_count
    FROM complaint
    GROUP BY customer_id
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY cc.complaint_count DESC, c.customer_id ASC) AS customer_rank, --lowest customer_id always wins if tie
    c.customer_id,
    c.first_name,
    c.last_name,
    cc.complaint_count
FROM customer_counts AS cc
JOIN customer AS c
    ON cc.customer_id = c.customer_id
ORDER BY customer_rank;

--8.Rank complaints by receive date within each category
SELECT ROW_NUMBER() OVER (ORDER BY 
CASE priority
	WHEN 'Critical' THEN 1
	WHEN 'High' THEN 2
	WHEN 'Medium' THEN 3
	WHEN 'Low' THEN 4
END ASC, received_at ASC) rank, priority, complaint_id, received_at
FROM complaint;

