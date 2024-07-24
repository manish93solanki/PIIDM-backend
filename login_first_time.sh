curl --location --request GET 'http://localhost:3002/api/user_role/all'

curl --location --request POST 'http://localhost:3002/api/user_role/add' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "name": "super_admin"
    },
    {
        "name": "agent"
    },
    {
        "name": "student"
    },
    {
        "name": "trainer"
    },
    {
        "name": "lead_distributor"
    },
    {
        "name": "hr"
    }
]'

curl --location --request POST 'http://localhost:3002/api/user/add' \
--header 'Content-Type: application/json' \
--data-raw '
    {
        "name": "admin",
        "phone_num": "+91-0000000000",
        "email": "admin@test.com",
        "password": "admin123",
        "user_role_id": 1
    }
'

curl --location --request POST 'http://localhost:3002/api/user/add' \
--header 'Content-Type: application/json' \
--data-raw '
    {
        "name": "Lead Distributor",
        "phone_num": "+91-0000000001",
        "email": "leads@test.com",
        "password": "ld123",
        "user_role_id": 5
    }
'

curl --location 'http://localhost:3002/api/user/add' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "trainer_admin",
    "phone_num": "+91-0000000001",
    "email": "trainer_admin@test.com",
    "password": "trainer123",
    "user_role_id": 4
}'


output=$(curl --location --request POST 'http://localhost:3002/api/user/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "admin@test.com",
    "password": "vjadmin4321"
}')
echo "$output"