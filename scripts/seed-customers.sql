-- Update customers with complete data for delivery notes
-- Update KD-10001
UPDATE domain_crm.customers SET 
    address = 'Musterstrasse 12',
    postal_code = '12345',
    city = 'Musterstadt',
    country = 'DE',
    phone = '+49 123 456789',
    email = 'mueller@landwirtschaft.de'
WHERE customer_number = 'KD-10001';

-- Update KD-10002
UPDATE domain_crm.customers SET 
    address = 'Bauernweg 5',
    postal_code = '37073',
    city = 'Goettingen',
    country = 'DE',
    phone = '+49 551 123456',
    email = 'info@hof-janssen.de'
WHERE customer_number = 'KD-10002';

-- Update KD-10003
UPDATE domain_crm.customers SET 
    address = 'Marktplatz 1',
    postal_code = '26919',
    city = 'Brake',
    country = 'DE',
    phone = '+49 4401 987654',
    email = 'kontakt@agrar-wesermarsch.de'
WHERE customer_number = 'KD-10003';

SELECT customer_number, company_name, city, postal_code, address, email FROM domain_crm.customers ORDER BY customer_number;
