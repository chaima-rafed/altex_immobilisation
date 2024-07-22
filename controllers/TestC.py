import json
import requests
import sys

AUTH_URL = 'http://localhost:8069/auth/'

headers = {'Content-type': 'application/json'}


# Remember to configure default db on odoo configuration file(dbfilter = ^db_name$)
# Authentication credentials
data = {
    'params': {
         'login': 'nesreddineboudene@gmail.com',
         'password': 'altexodoo23',
         'db': 'pos_alg_ferries'
    }
}

# Authenticate user
res = requests.post(
    AUTH_URL,
    data=json.dumps(data),
    headers=headers
)

# Get response cookies
# This hold information for authenticated user
cookies = res.cookies


# Example 1
# Get users
USERS_URL = 'http://localhost:8069/api/res.users/'

# This will take time since it retrives all res.users fields
# You can use query param to fetch specific fields

res = requests.get(
    USERS_URL,
    cookies=cookies  # Here we are sending cookies which holds info for authenticated user
)

# This will be a very long response since it has many data
print(res.text)


# Example 2
# Get products(assuming you have products in you db)
# Here am using query param to fetch only product id and name(This will be faster)
USERS_URL = 'http://localhost:8069/api/product.product/'

# Use query param to fetch only id and name
params = {'query': '{id, name}'}

res = requests.get(
    USERS_URL,
    params=params,
    cookies=cookies  # Here we are sending cookies which holds info for authenticated user
)

# This will be small since we've retrieved only id and name
print(res.text)