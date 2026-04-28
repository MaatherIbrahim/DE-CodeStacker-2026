# Design Reflection

## Critical Issues

### What was the most critical issue you discovered?
data are not correct in the final report due to duplicate, uncounted, null values and those values are counted to be in the last analytic table which could cause wrong analysis report

---

## Trade-offs

### What trade-offs did you make?
I make sure that the data  get in the staging tables where unique which basically removed the dupliactes then insert the data, also make sure there is no null values in the most important columns, and the uncounted values where removed

---

## Failure Scenarios

### Where could your solution still fail?
for this case no but if there any changes in the API it will raise an error 


---

## Scalability

### How would this system behave at 100x data volume?
It could fail due to memory limit because all the files and the pipeline store in the memory

---

## Future Improvements

### What would you redesign with more time?

make the backup saves as csv files and the queries if there  any saved as text file and the database saved as sql file as is it now

## Deep Dives

### Explain one complex function line-by-line
cus_id = shipment.get('customer_id'):
use .get() to safly check for the id without crashing if the key is missing

ON CONFLICT (shipment_id) DO UPDATE SET:
if the task is rerun it update existing shipment status instead of creating duplicate row

### Explain one SQL transformation step-by-step
TRUNCATE TABLE analytics.shipping_spend_by_tier: ensure the target table is empty so that rerunning the pipeline never results in duplicate sums

### Describe one alternative design you considered and rejected
I considered using SCD Type 2 (Historical Tracking) for shipment status changes. This would involve adding valid_from and valid_to columns to track every time a shipment moved from 'Pending' to 'Delivered'. I rejected this because the primary business requirement was Total Shipping Spend per Month. Summing costs across multiple historical rows for the same shipment would lead to Double Counting, making the financial report inaccurate. I chose SCD Type 1 (Overwrite) to prioritize financial accuracy.
